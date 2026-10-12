use anchor_lang::prelude::*;
use anchor_spl::token_interface::{Mint, TokenAccount, TokenInterface};

declare_id!("Xu7JJXtKWyA1LfNpc1tcCNfEiZJQQYWn5Ymo96j9vHa"); // Replace with the program ID from the instructor's template before build/deploy.

#[program]
pub mod liquidity_vault {
    use super::*;

    /// Chapter 8 scaffold: initialize configuration, program-controlled share mint,
    /// and underlying-token vault. No deposit/swap/CLMM behavior is implemented.
    pub fn create_vault(ctx: Context<CreateVault>) -> Result<()> {
        let config = &mut ctx.accounts.config;
        config.admin = ctx.accounts.admin.key();
        config.underlying_mint = ctx.accounts.underlying_mint.key();
        config.share_mint = ctx.accounts.share_mint.key();
        config.vault_authority_bump = ctx.bumps.vault_authority;
        config.total_deposited = 0;
        Ok(())
    }

    /// Create the user's PDA card. Chapter 8 only: no token movement or position value yet.
    pub fn open_position(ctx: Context<OpenPosition>) -> Result<()> {
        let position = &mut ctx.accounts.position;
        position.user = ctx.accounts.user.key();
        position.config = ctx.accounts.config.key();
        position.deposited_amount = 0;
        position.bump = ctx.bumps.position;
        Ok(())
    }
}

#[derive(Accounts)]
pub struct CreateVault<'info> {
    #[account(init, payer = admin, space = 8 + VaultConfig::INIT_SPACE, seeds = [b"config", admin.key().as_ref()], bump)]
    pub config: Account<'info, VaultConfig>,
    /// CHECK: PDA authority used as token-account and mint authority; no data is read.
    #[account(seeds = [b"vault-authority", config.key().as_ref()], bump)]
    pub vault_authority: UncheckedAccount<'info>,
    pub underlying_mint: InterfaceAccount<'info, Mint>,
    #[account(
        init, payer = admin, mint::decimals = underlying_mint.decimals,
        mint::authority = vault_authority, seeds = [b"share", config.key().as_ref()], bump
    )]
    pub share_mint: InterfaceAccount<'info, Mint>,
    #[account(
        init, payer = admin, token::mint = underlying_mint,
        token::authority = vault_authority, seeds = [b"token-vault", config.key().as_ref()], bump
    )]
    pub token_vault: InterfaceAccount<'info, TokenAccount>,
    #[account(mut)]
    pub admin: Signer<'info>,
    pub token_program: Interface<'info, TokenInterface>,
    pub system_program: Program<'info, System>,
    pub rent: Sysvar<'info, Rent>,
}

#[derive(Accounts)]
pub struct OpenPosition<'info> {
    #[account(seeds = [b"config", config.admin.as_ref()], bump)]
    pub config: Account<'info, VaultConfig>,
    #[account(init, payer = user, space = 8 + UserPosition::INIT_SPACE, seeds = [b"position", config.key().as_ref(), user.key().as_ref()], bump)]
    pub position: Account<'info, UserPosition>,
    #[account(mut)]
    pub user: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[account]
#[derive(InitSpace)]
pub struct VaultConfig {
    pub admin: Pubkey,
    pub underlying_mint: Pubkey,
    pub share_mint: Pubkey,
    pub vault_authority_bump: u8,
    pub total_deposited: u64,
}

#[account]
#[derive(InitSpace)]
pub struct UserPosition {
    pub user: Pubkey,
    pub config: Pubkey,
    pub deposited_amount: u64,
    pub bump: u8,
}

#[error_code]
pub enum VaultError {
    #[msg("Only the configured administrator may perform this action")]
    Unauthorized,
}

// This is a preparation scaffold, not the instructor's unpublished starter and not yet audited.
// Before using: set a real program ID, generate Anchor IDL, add account constraints/tests,
// and verify account ordering against the provided template when it arrives.
// Weeks 9-15 features (deposit/withdraw CPI, swaps, CLMM positions/fees) are intentionally absent.

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn account_space_is_sized_for_fixed_fields() {
        assert_eq!(VaultConfig::INIT_SPACE, 32 * 3 + 1 + 8);
        assert_eq!(UserPosition::INIT_SPACE, 32 * 2 + 8 + 1);
    }
}
