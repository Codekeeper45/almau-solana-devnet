import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {Connection,Keypair,PublicKey,SystemProgram,SYSVAR_CLOCK_PUBKEY,SYSVAR_RENT_PUBKEY,Transaction,TransactionInstruction} from '@solana/web3.js';
import {assertDevnet} from './create-pool.mjs';
const c=new Connection(process.env.DEVNET_RPC || 'https://api.devnet.solana.com',{commitment:'confirmed',disableRetryOnRateLimit:true});
const delay=ms=>new Promise(resolve=>setTimeout(resolve,ms));
let nextRpc=0;
async function paced(fn){
 const now=Date.now(), start=Math.max(now,nextRpc); nextRpc=start+420;
 if(start>now)await delay(start-now);
 for(let n=0;;n++){
  try{return await fn();}catch(e){if(n>=5||!/429|502|503|504|fetch failed/i.test(String(e)))throw e;await delay(2500*(n+1));}
 }
}
await assertDevnet(c);
const key=p=>Keypair.fromSecretKey(Uint8Array.from(JSON.parse(readFileSync(p))));
const wallet=key(process.env.ANCHOR_WALLET), program=key(process.env.PROGRAM_KEY);
assert.equal(String(program.publicKey),'EGrtYqUVMoRxGbQj6YT5KhYNTdNQsybBjidq8zVJiahQ');
const elf=readFileSync(process.argv[2]); assert.equal(elf.subarray(0,4).toString('hex'),'7f454c46');
const L=new PublicKey('BPFLoaderUpgradeab1e11111111111111111111111');
const m=(pubkey,isWritable=false,isSigner=false)=>({pubkey,isWritable,isSigner});
function u32(x){const b=Buffer.alloc(4);b.writeUInt32LE(x);return b;}
function u64(x){const b=Buffer.alloc(8);b.writeBigUInt64LE(BigInt(x));return b;}
const ix=(n,keys,...d)=>new TransactionInstruction({programId:L,keys,data:Buffer.concat([u32(n),...d])});
async function send(instructions,signers=[]){
 const bh=await paced(()=>c.getLatestBlockhash()); const tx=new Transaction({feePayer:wallet.publicKey,...bh}).add(...instructions);tx.sign(wallet,...signers);
 const signature=await paced(()=>c.sendRawTransaction(tx.serialize()));
 for(let attempt=0;attempt<45;attempt++){
  const {value:[status]}=await paced(()=>c.getSignatureStatuses([signature]));
  if(status){assert.equal(status.err,null,signature);if(['confirmed','finalized'].includes(status.confirmationStatus))return signature;}
  await delay(900);
 }
 throw new Error(`Confirmation timed out: ${signature}`);
}
const [pd]=PublicKey.findProgramAddressSync([program.publicKey.toBytes()],L);
const previous=await c.getAccountInfo(program.publicKey);
const deployed=previous?.executable ? await c.getAccountInfo(pd) : null;
if(!deployed?.data.subarray(45,45+elf.length).equals(elf)){
 const bufferPath=process.env.PROGRAM_KEY+(deployed?'.upgrade-buffer':'.buffer'); let buffer;
 try {buffer=key(bufferPath);} catch(e){if(e.code!=='ENOENT') throw e;buffer=Keypair.generate();writeFileSync(bufferPath,JSON.stringify([...buffer.secretKey]),{mode:0o600,flag:'wx'});}
 const size=elf.length+37;
 const rent=await c.getMinimumBalanceForRentExemption(size);
 const programRent=await c.getMinimumBalanceForRentExemption(36);
 const dataRent=await c.getMinimumBalanceForRentExemption(elf.length+45);
 if(deployed){assert.ok(deployed.data.subarray(13,45).equals(wallet.publicKey.toBuffer()),'Unexpected upgrade authority');}
 const additional=deployed&&elf.length>deployed.data.length-45 ? Math.max(10000,elf.length+45-deployed.data.length) : 0;
 const extensionRent=additional?Math.max(0,(await c.getMinimumBalanceForRentExemption(deployed.data.length+additional))-deployed.lamports):0;
 const existing=await c.getAccountInfo(buffer.publicKey);
 const required=(deployed?0:programRent+dataRent)+Math.max(0,rent-(existing?.lamports||0))+extensionRent;
 assert.ok(await c.getBalance(wallet.publicKey)>required+0.05e9,'Insufficient Devnet SOL for program rent');
 if(additional)console.log('extend',await send([ix(9,[m(pd,true),m(program.publicKey,true),m(wallet.publicKey,true,true),m(SystemProgram.programId),m(wallet.publicKey,true,true)],u32(additional))]));
 if(!existing)await send([SystemProgram.createAccount({fromPubkey:wallet.publicKey,newAccountPubkey:buffer.publicKey,space:size,lamports:rent,programId:L}),ix(0,[m(buffer.publicKey,true),m(wallet.publicKey)])],[buffer]);
 const saved=(await c.getAccountInfo(buffer.publicKey)).data;
 for(let i=0;i<elf.length;){
  const batch=[];
  for(let j=0;j<2&&i<elf.length;j++,i+=950){const chunk=elf.subarray(i,i+950);if(!saved.subarray(37+i,37+i+chunk.length).equals(chunk))batch.push(ix(1,[m(buffer.publicKey,true),m(wallet.publicKey,false,true)],u32(i),u64(chunk.length),chunk));}
  if(batch.length){
   for(let attempt=0;;attempt++){
    const results=await Promise.allSettled(batch.map(x=>send([x])));const fail=results.find(x=>x.status==='rejected');
    if(!fail)break;
    if(attempt>=3||!/429|block height exceeded|timed out/i.test(String(fail.reason)))throw fail.reason;
    await new Promise(r=>setTimeout(r,3000*(attempt+1)));
   }
   await new Promise(r=>setTimeout(r,650));
  }
  if(i%57000===0||i>=elf.length) console.log('uploaded',Math.min(i,elf.length),elf.length);
 }
 assert.ok((await c.getAccountInfo(buffer.publicKey)).data.subarray(37).equals(elf));
 const sig=deployed
  ?await send([ix(3,[m(pd,true),m(program.publicKey,true),m(buffer.publicKey,true),m(wallet.publicKey,true),m(SYSVAR_RENT_PUBKEY),m(SYSVAR_CLOCK_PUBKEY),m(wallet.publicKey,false,true)])])
  :await send([SystemProgram.createAccount({fromPubkey:wallet.publicKey,newAccountPubkey:program.publicKey,space:36,lamports:programRent,programId:L}),ix(2,[m(wallet.publicKey,true,true),m(pd,true),m(program.publicKey,true),m(buffer.publicKey,true),m(SYSVAR_RENT_PUBKEY),m(SYSVAR_CLOCK_PUBKEY),m(SystemProgram.programId),m(wallet.publicKey,false,true)],u64(elf.length))],[program]);
 console.log(deployed?'upgrade':'deploy',sig);
}
const account=await c.getAccountInfo(program.publicKey);assert.ok(account?.executable&&account.owner.equals(L));
assert.ok((await c.getAccountInfo(pd)).data.subarray(45,45+elf.length).equals(elf));
console.log('Verified Devnet executable and byte-for-byte ProgramData',String(program.publicKey));
