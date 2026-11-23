import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync, writeFileSync} from 'node:fs';
import {Connection, Keypair, PublicKey, SystemProgram, SYSVAR_RENT_PUBKEY, Transaction, TransactionInstruction, sendAndConfirmTransaction} from '@solana/web3.js';
import {createMint,getOrCreateAssociatedTokenAccount,mintTo,getAccount,TOKEN_PROGRAM_ID} from '@solana/spl-token';
const c=new Connection(process.env.DEVNET_RPC || 'https://api.devnet.solana.com','confirmed');
assert.equal(await c.getGenesisHash(),'EtWTRABZaYq6iMfeYKouRu166VU2xqa1wcaWoxPkrZBG');
const program=new PublicKey('EGrtYqUVMoRxGbQj6YT5KhYNTdNQsybBjidq8zVJiahQ');
assert.ok((await c.getAccountInfo(program))?.executable);
const w=Keypair.fromSecretKey(Uint8Array.from(JSON.parse(readFileSync(process.env.ANCHOR_WALLET))));
// Fresh mint isolates this exercise from the shared Raydium demo vault.
const mint=await createMint(c,w,w.publicKey,null,6);
const p=(name,...parts)=>PublicKey.findProgramAddressSync([Buffer.from(name),...parts.map(k=>k.toBuffer())],program)[0];
const state=p('vault',mint),base=p('vault_tokens',mint),share=p('share_mint',mint),card=p('user_card',state,w.publicKey);
const k=(pubkey,isWritable=false,isSigner=false)=>({pubkey,isWritable,isSigner});
const ix=(name,keys,amount)=>{
 const data=Buffer.alloc(amount===undefined?8:16);
 createHash('sha256').update('global:'+name).digest().copy(data,0,0,8);
 if(amount!==undefined)data.writeBigUInt64LE(amount,8);
 return new TransactionInstruction({programId:program,keys,data});
};
const send=(...ixs)=>sendAndConfirmTransaction(c,new Transaction().add(...ixs),[w],{commitment:'confirmed'});
const init=await send(ix('initialize_vault',[k(state,true),k(base,true),k(share,true),k(mint),k(w.publicKey,true,true),k(TOKEN_PROGRAM_ID),k(SystemProgram.programId),k(SYSVAR_RENT_PUBKEY)]),ix('create_user_card',[k(state),k(card,true),k(w.publicKey,true,true),k(SystemProgram.programId)]));
const userBase=(await getOrCreateAssociatedTokenAccount(c,w,mint,w.publicKey)).address;
const userShare=(await getOrCreateAssociatedTokenAccount(c,w,share,w.publicKey)).address;
await mintTo(c,w,mint,userBase,w,10_000_000n);
const keys=[k(state,true),k(card,true),k(base,true),k(share,true),k(userBase,true),k(userShare,true),k(w.publicKey,true,true),k(TOKEN_PROGRAM_ID)];
const balances=()=>Promise.all([userBase,userShare,base].map(async a=>(await getAccount(c,a)).amount));
const deposit=await send(ix('deposit',keys,8_000_000n));
assert.deepEqual(await balances(),[2_000_000n,8_000_000n,8_000_000n]);
await assert.rejects(send(ix('withdraw',keys,0n)),/ZeroAmount|Amount must be greater|0x177/i);
assert.deepEqual(await balances(),[2_000_000n,8_000_000n,8_000_000n]);
const withdraw=await send(ix('withdraw',keys,3_000_000n));
assert.deepEqual(await balances(),[5_000_000n,5_000_000n,5_000_000n]);
const recover=await send(ix('withdraw',keys,5_000_000n));
assert.deepEqual(await balances(),[10_000_000n,0n,0n]);
let parsed;
for(let i=0;i<20 && !parsed;i++){
 parsed=await c.getParsedTransaction(withdraw,{commitment:'confirmed',maxSupportedTransactionVersion:0});
 if(!parsed) await new Promise(r=>setTimeout(r,1200));
}
assert.equal(parsed?.meta?.err,null);
const cpis=parsed.meta.innerInstructions.flatMap(x=>x.instructions).filter(x=>x.programId.equals(TOKEN_PROGRAM_ID)).map(x=>({type:x.parsed?.type,amount:x.parsed?.info?.amount}));
assert.deepEqual(cpis,[{type:'burn',amount:'3000000'},{type:'transfer',amount:'3000000'}]);
const out={network:'devnet',program:String(program),mint:String(mint),vault:String(state),init,deposit,withdraw,recover,slot:parsed.slot,cpis};
writeFileSync(new URL('./evidence/devnet-withdraw.json',import.meta.url),JSON.stringify(out,null,2)+'\n');
console.log(JSON.stringify(out,null,2));
