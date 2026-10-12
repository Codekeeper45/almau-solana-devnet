use std::{env, error::Error, fmt, process::Command};
#[derive(Debug)]
struct RpcRequest { method: String, params: String }
#[derive(Debug)]
enum LabError { Usage, InvalidAddress, InvalidSignature, Transport(String) }
impl fmt::Display for LabError { fn fmt(&self,f:&mut fmt::Formatter<'_>)->fmt::Result { match self { Self::Transport(message)=>write!(f,"Transport: {}",message), _=>write!(f,"{:?}",self) } } }
impl Error for LabError {}
fn base58_len(s:&str)->Result<usize,LabError> {
    let alphabet=b"123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";
    let mut bytes:Vec<u8>=vec![];
    for ch in s.bytes() {
        let mut carry=alphabet.iter().position(|c|*c==ch).ok_or(LabError::InvalidAddress)? as u32;
        for byte in bytes.iter_mut().rev() { carry+=(*byte as u32)*58; *byte=(carry&255) as u8; carry>>=8; }
        while carry>0 {bytes.insert(0,(carry&255) as u8);carry>>=8;}
    }
    Ok(bytes.len()+s.bytes().take_while(|c|*c==b'1').count())
}
fn request(args:&[String])->Result<RpcRequest,LabError> {
    match args {
        [cmd,address] if cmd=="balance"=> {
            if base58_len(address)?!=32 {return Err(LabError::InvalidAddress)}
            Ok(RpcRequest{method:"getBalance".into(),params:format!("[\"{}\",{{\"commitment\":\"confirmed\"}}]",address)})
        },
        [cmd,sig] if cmd=="transaction"=> {
            if base58_len(sig).map_err(|_|LabError::InvalidSignature)?!=64 {return Err(LabError::InvalidSignature)}
            Ok(RpcRequest{method:"getTransaction".into(),params:format!("[\"{}\",{{\"encoding\":\"jsonParsed\",\"maxSupportedTransactionVersion\":0,\"commitment\":\"confirmed\"}}]",sig)})
        },
        _=>Err(LabError::Usage)
    }
}
fn execute(req:&RpcRequest)->Result<String,LabError> {
    let payload=format!("{{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"{}\",\"params\":{}}}",req.method,req.params);
    let output=Command::new("curl").args(["--fail-with-body","--silent","--show-error","--max-time","30","https://api.devnet.solana.com","-H","Content-Type: application/json","--data",&payload]).output().map_err(|e|LabError::Transport(e.to_string()))?;
    if !output.status.success() {return Err(LabError::Transport(String::from_utf8_lossy(&output.stderr).into()))}
    String::from_utf8(output.stdout).map_err(|e|LabError::Transport(e.to_string()))
}
fn main()->Result<(),Box<dyn Error>> {
    let args:Vec<String>=env::args().skip(1).collect();
    let req=request(&args).map_err(|e|{eprintln!("Usage: solana-lab-cli balance <32-byte pubkey> | transaction <64-byte signature>");e})?;
    println!("{}",execute(&req)?); Ok(())
}
#[cfg(test)] mod tests {
    use super::*;
    #[test] fn system_address(){assert_eq!(base58_len("11111111111111111111111111111111").unwrap(),32)}
    #[test] fn invalid_chars(){assert!(base58_len("Coll9Xz").is_err())}
    #[test] fn short_signature(){assert!(request(&["transaction".into(),"111".into()]).is_err())}
    #[test] fn valid_balance(){assert!(request(&["balance".into(),"2SzJ2PSuhnQsenfvHK4DhQHibjVL2d68fwdHAMwxJ7pL".into()]).is_ok())}
    #[test] fn usage(){assert!(request(&[]).is_err())}
}
