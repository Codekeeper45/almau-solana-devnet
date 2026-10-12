use anchor_lang::prelude::*;

declare_id!("Fg6PaFpoGXkYsidMpWxTWqkZ8q7kL6K2f3d9c8P4v1A");

#[program]
pub mod anchor_counter {
    use super::*;
    pub fn initialize(ctx: Context<Initialize>) -> Result<()> {
        ctx.accounts.counter.authority = ctx.accounts.authority.key();
        ctx.accounts.counter.count = 0;
        Ok(())
    }
    pub fn increment(ctx: Context<UpdateCounter>) -> Result<()> {
        ctx.accounts.counter.count = ctx.accounts.counter.count.checked_add(1).ok_or(CounterError::Overflow)?;
        Ok(())
    }
    pub fn decrement(ctx: Context<UpdateCounter>) -> Result<()> {
        ctx.accounts.counter.count = ctx.accounts.counter.count.checked_sub(1).ok_or(CounterError::Underflow)?;
        Ok(())
    }
}

#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(init, payer = authority, space = 8 + Counter::INIT_SPACE)]
    pub counter: Account<'info, Counter>,
    #[account(mut)]
    pub authority: Signer<'info>,
    pub system_program: Program<'info, System>,
}
#[derive(Accounts)]
pub struct UpdateCounter<'info> {
    #[account(mut, has_one = authority)]
    pub counter: Account<'info, Counter>,
    pub authority: Signer<'info>,
}
#[account]
#[derive(InitSpace)]
pub struct Counter { pub authority: Pubkey, pub count: u64 }
#[error_code]
pub enum CounterError { #[msg("counter overflow")] Overflow, #[msg("counter cannot be negative")] Underflow }

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
    fn counter_client_roundtrip_and_authority_check() {
        let authority = Pubkey::new_unique();
        let attacker = Pubkey::new_unique();
        let counter_key = Pubkey::new_unique();
        let system_key = anchor_lang::system_program::ID;
        let (mut l1, mut l2, mut l3, mut l4) = (2_000_000u64, 2_000_000u64, 2_000_000u64, 1u64);
        let mut buf = vec![0u8; 8 + Counter::INIT_SPACE];
        let mut empty1 = [];
        let mut empty2 = [];
        let mut empty3 = [];
        let c = account(&counter_key, &ID, &mut l1, &mut buf, true, true);
        let a = account(&authority, &system_key, &mut l2, &mut empty1, true, true);
        let u = account(&attacker, &system_key, &mut l3, &mut empty2, true, false);
        let mut sys = account(&system_key, &system_key, &mut l4, &mut empty3, false, false);
        sys.executable = true;
        {
            let mut slice = &mut c.try_borrow_mut_data().unwrap()[..];
            Counter { authority, count: 0 }.try_serialize(&mut slice).unwrap();
        }
        let valid = [c.clone(), a];
        let invalid = [c.clone(), u];
        entry(&ID, &valid, &instruction::Increment {}.data()).unwrap();
        entry(&ID, &valid, &instruction::Increment {}.data()).unwrap();
        let state = Counter::try_deserialize(&mut &c.try_borrow_data().unwrap()[..]).unwrap();
        assert_eq!(state.count, 2);
        assert!(entry(&ID, &invalid, &instruction::Increment {}.data()).is_err());
        entry(&ID, &valid, &instruction::Decrement {}.data()).unwrap();
        entry(&ID, &valid, &instruction::Decrement {}.data()).unwrap();
        assert!(entry(&ID, &valid, &instruction::Decrement {}.data()).is_err());
    }
}
