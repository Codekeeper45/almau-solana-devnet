use anchor_lang::prelude::*;
declare_id!("Fg6PaFpoGXkYsidMpWxTWqkZ8q7kL6K2f3d9c8P4v1B");
#[program]
pub mod pda_profile {
    use super::*;
    pub fn create_profile(ctx: Context<CreateProfile>, username: String, bio: String) -> Result<()> {
        require!(username.len() <= 32, ProfileError::UsernameTooLong);
        require!(bio.len() <= 160, ProfileError::BioTooLong);
        let profile = &mut ctx.accounts.profile;
        profile.authority = ctx.accounts.authority.key();
        profile.username = username;
        profile.bio = bio;
        profile.bump = ctx.bumps.profile;
        Ok(())
    }
    pub fn update_profile(ctx: Context<UpdateProfile>, username: String, bio: String) -> Result<()> {
        require!(username.len() <= 32, ProfileError::UsernameTooLong);
        require!(bio.len() <= 160, ProfileError::BioTooLong);
        let profile = &mut ctx.accounts.profile;
        profile.username = username;
        profile.bio = bio;
        Ok(())
    }
}
#[derive(Accounts)]
pub struct CreateProfile<'info> {
    #[account(init, payer = authority, space = 8 + UserProfile::INIT_SPACE, seeds = [b"profile", authority.key().as_ref()], bump)]
    pub profile: Account<'info, UserProfile>,
    #[account(mut)]
    pub authority: Signer<'info>,
    pub system_program: Program<'info, System>,
}
#[derive(Accounts)]
pub struct UpdateProfile<'info> {
    #[account(mut, has_one = authority, seeds = [b"profile", authority.key().as_ref()], bump = profile.bump)]
    pub profile: Account<'info, UserProfile>,
    pub authority: Signer<'info>,
}
#[account]
#[derive(InitSpace)]
pub struct UserProfile {
    pub authority: Pubkey,
    #[max_len(32)]
    pub username: String,
    #[max_len(160)]
    pub bio: String,
    pub bump: u8,
}
#[error_code]
pub enum ProfileError {
    #[msg("username exceeds 32 bytes")]
    UsernameTooLong,
    #[msg("bio exceeds 160 bytes")]
    BioTooLong,
}

#[cfg(test)]
mod tests {
    use super::*;
    use anchor_lang::InstructionData;
    use std::cell::RefCell;
    use std::rc::Rc;

    fn account<'a>(key: &'a Pubkey, owner: &'a Pubkey, lamports: &'a mut u64, data: &'a mut [u8], signer: bool, writable: bool) -> AccountInfo<'a> {
        AccountInfo { key, is_signer: signer, is_writable: writable, lamports: Rc::new(RefCell::new(lamports)), data: Rc::new(RefCell::new(data)), owner, executable: false, rent_epoch: 0 }
    }

    #[test]
    fn pda_derivation_update_and_owner_check() {
        let authority = Pubkey::new_unique();
        let attacker = Pubkey::new_unique();
        let (pda, bump) = Pubkey::find_program_address(&[b"profile", authority.as_ref()], &ID);
        let recreated = Pubkey::create_program_address(&[b"profile", authority.as_ref(), &[bump]], &ID).unwrap();
        assert_eq!(pda, recreated);
        let (mut l1, mut l2, mut l3) = (3_000_000u64, 2_000_000u64, 2_000_000u64);
        let mut buf = vec![0u8; 8 + UserProfile::INIT_SPACE];
        let mut empty1 = [];
        let mut empty2 = [];
        let p = account(&pda, &ID, &mut l1, &mut buf, false, true);
        let a = account(&authority, &anchor_lang::system_program::ID, &mut l2, &mut empty1, true, true);
        let u = account(&attacker, &anchor_lang::system_program::ID, &mut l3, &mut empty2, true, false);
        {
            let mut slice = &mut p.try_borrow_mut_data().unwrap()[..];
            UserProfile { authority, username: "emir".into(), bio: "Data Science".into(), bump }.try_serialize(&mut slice).unwrap();
        }
        let valid = [p.clone(), a];
        let invalid = [p.clone(), u];
        entry(&ID, &valid, &instruction::UpdateProfile { username: "emir_ds".into(), bio: "AlmaU 3 course".into() }.data()).unwrap();
        let state = UserProfile::try_deserialize(&mut &p.try_borrow_data().unwrap()[..]).unwrap();
        assert_eq!(state.username, "emir_ds");
        assert_eq!(state.bio, "AlmaU 3 course");
        assert!(entry(&ID, &invalid, &instruction::UpdateProfile { username: "hack".into(), bio: "bad".into() }.data()).is_err());
        assert!(entry(&ID, &valid, &instruction::UpdateProfile { username: "x".repeat(33), bio: "ok".into() }.data()).is_err());
    }
}
