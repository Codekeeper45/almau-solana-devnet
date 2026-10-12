//! Week 4: minimal Solana program. Instruction byte `0` logs a greeting.
use solana_program::{account_info::AccountInfo, entrypoint, entrypoint::ProgramResult, msg, pubkey::Pubkey};

entrypoint!(process_instruction);

pub fn process_instruction(_program_id: &Pubkey, _accounts: &[AccountInfo], data: &[u8]) -> ProgramResult {
    match data {
        [0] => { msg!("Hello from Emir's first Solana program!"); Ok(()) },
        _ => Err(solana_program::program_error::ProgramError::InvalidInstructionData),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn greeting_instruction_succeeds() {
        let id = Pubkey::new_unique();
        assert!(process_instruction(&id, &[], &[0]).is_ok());
    }
    #[test]
    fn unknown_instruction_fails() {
        let id = Pubkey::new_unique();
        assert_eq!(process_instruction(&id, &[], &[1]), Err(solana_program::program_error::ProgramError::InvalidInstructionData));
    }
}
