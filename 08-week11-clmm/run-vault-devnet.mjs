import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {Connection,Keypair,PublicKey,ComputeBudgetProgram,SystemProgram,SYSVAR_RENT_PUBKEY,TransactionInstruction,TransactionMessage,VersionedTransaction} from '@solana/web3.js';
import {getAccount,getAssociatedTokenAddressSync,getOrCreateAssociatedTokenAccount,TOKEN_PROGRAM_ID,TOKEN_2022_PROGRAM_ID,createTransferInstruction} from '@solana/spl-token';
import {ClmmInstrument,Raydium,DEV_API_URLS,PoolUtils,PositionInfoLayout,TickUtils,getPdaPersonalPositionAddress,getPdaProtocolPositionAddress,getPdaTickArrayAddress} from '@raydium-io/raydium-sdk-v2';
import BN from 'bn.js';
import {assertDevnet} from './create-pool.mjs';

const c=new Connection(process.env.DEVNET_RPC||'https://api.devnet.solana.com','confirmed');
await assertDevnet(c);
const key=p=>Keypair.fromSecretKey(Uint8Array.from(JSON.parse(readFileSync(p))));
const w=key(process.env.ANCHOR_WALLET), program=new PublicKey('EGrtYqUVMoRxGbQj6YT5KhYNTdNQsybBjidq8zVJiahQ');
const {poolId,clmmProgram,tokenA,tokenB,ammConfig}=JSON.parse(readFileSync(new URL('./evidence/devnet-pool.json',import.meta.url)));
const [P,R,A,B,C]=[poolId,clmmProgram,tokenA,tokenB,ammConfig].map(x=>new PublicKey(x));
const pda=(name,...parts)=>PublicKey.findProgramAddressSync([Buffer.from(name),...parts.map(x=>x.toBuffer())],program)[0];
const state=pda('vault',A),base=pda('vault_tokens',A),share=pda('share_mint',A),card=pda('user_card',state,w.publicKey);
const quote=getAssociatedTokenAddressSync(B,state,true), userA=getAssociatedTokenAddressSync(A,w.publicKey), userShare=getAssociatedTokenAddressSync(share,w.publicKey);
const hash=n=>createHash('sha256').update(`global:${n}`).digest().subarray(0,8);
const m=(pubkey,isWritable=false,isSigner=false)=>({pubkey,isWritable,isSigner});
const u=(x,size)=>new BN(String(x)).toArrayLike(Buffer,'le',size);
const i=x=>{const b=Buffer.alloc(4);b.writeInt32LE(x);return b;};
const own=(n,keys,...body)=>new TransactionInstruction({programId:program,keys,data:Buffer.concat([hash(n),...body])});
const strategy=(n,ray,signer=w.publicKey,...body)=>own(n,[m(signer,false,true),m(state,true),m(base,true),m(quote,true),m(R),...ray.keys.map(k=>k.pubkey.equals(state)?{...k,isSigner:false}:k)],...body);
async function send(ixs,signers=[w],error){
 const bh=await c.getLatestBlockhash(); const tx=new VersionedTransaction(new TransactionMessage({payerKey:w.publicKey,recentBlockhash:bh.blockhash,instructions:[ComputeBudgetProgram.setComputeUnitLimit({units:950000}),...ixs]}).compileToV0Message());
 tx.sign([...new Map([w,...signers].map(k=>[String(k.publicKey),k])).values()]);
 const signature=await c.sendRawTransaction(tx.serialize(),{skipPreflight:!!error});
 let evidence;
 for(let attempt=0;attempt<55;attempt++){
  try{evidence=await c.getTransaction(signature,{commitment:'finalized',maxSupportedTransactionVersion:0});}
  catch(e){if(!/429|502|503|504|fetch failed/i.test(String(e)))throw e;}
  if(evidence?.meta)break;
  await new Promise(r=>setTimeout(r,1100));
 }
 assert.ok(evidence?.meta,`Finalized transaction unavailable: ${signature}`);
 const logs=evidence.meta.logMessages.join('\n');
 if(error){assert.ok(evidence.meta.err,`Unexpected success: ${signature}`);assert.match(logs,error,`${signature}\n${logs}`);} else assert.equal(evidence.meta.err,null,`${signature}\n${logs}`);
 console.log(signature,error?'expected failure':'finalized');return signature;
}
const sdk=await Raydium.load({connection:c,owner:w,cluster:'devnet',urlConfigs:DEV_API_URLS,disableFeatureCheck:true,disableLoadToken:true});
const live=()=>sdk.clmm.getPoolInfoFromRpc(poolId);
const balance=async (a=base,b=quote)=>Promise.all([a,b].map(async k=>(await getAccount(c,k)).amount));
const outPath=new URL('./evidence/devnet-weeks12-13.json',import.meta.url);
const evidence=existsSync(outPath)?JSON.parse(readFileSync(outPath)):{program:String(program),poolId,vault:String(state)};
const save=()=>writeFileSync(outPath,JSON.stringify(evidence,null,2)+'\n');
assert.ok((await c.getAccountInfo(program))?.executable,'Program not deployed');
if(!await c.getAccountInfo(state))evidence.initialize=await send([own('initialize_vault',[m(state,true),m(base,true),m(share,true),m(A),m(w.publicKey,true,true),m(TOKEN_PROGRAM_ID),m(SystemProgram.programId),m(SYSVAR_RENT_PUBKEY)])]);
await getOrCreateAssociatedTokenAccount(c,w,B,state,true,'confirmed');
await getOrCreateAssociatedTokenAccount(c,w,share,w.publicKey,false,'confirmed');
if(!await c.getAccountInfo(card))evidence.card=await send([own('create_user_card',[m(state),m(card,true),m(w.publicKey,true,true),m(SystemProgram.programId)])]);
if(!evidence.deposit){evidence.deposit=await send([own('deposit',[m(state,true),m(card,true),m(base,true),m(share,true),m(userA,true),m(userShare,true),m(w.publicKey,false,true),m(TOKEN_PROGRAM_ID)],u(75_000_000,8))]);save();}

const swap=async (aToB,amount,signer=w,pair=[base,quote])=>{
 const {computePoolInfo:p,tickData,poolInfo}=await live();
 const inputMint=aToB?A:B; const n=new BN(String(amount));
 const q=PoolUtils.computeAmountOut({poolInfo:p,tickArrayCache:tickData[poolId],baseMint:inputMint,epochInfo:await c.getEpochInfo(),amountIn:n,slippage:0.01,catchLiquidityInsufficient:false});
 const min=q.minAmountOut.amount;
 const ix=(floor,payer)=>ClmmInstrument.swapInstruction(R,payer,P,C,pair[aToB?0:1],pair[aToB?1:0],aToB?p.vaultA:p.vaultB,aToB?p.vaultB:p.vaultA,inputMint,aToB?B:A,q.remainingAccounts,p.observationId,n,floor,new BN(0),true);
 return {q,min,ix,price:String(poolInfo.price),build:(floor=min,admin=w.publicKey)=>strategy('swap',ix(floor,state),admin,u(amount,8),u(floor,8),Buffer.from([+aToB]))};
};
if(!evidence.swap){
 const s=await swap(true,30_000_000); const before=await balance();
 const tooHigh=s.q.amountOut.amount.addn(1_000_000);
 const reject=await send([s.build(tooHigh)],[],/TooLittleOutputReceived|Price slippage check|Too little output/i);
 assert.deepEqual(await balance(),before);
 const tx=await send([s.build()]);const after=await balance();
 assert.equal(before[0]-after[0],30_000_000n);assert.ok(after[1]-before[1]>=BigInt(s.min.toString()));
 const end=await live(); assert.notEqual(String(end.poolInfo.price),s.price);
 evidence.swap={tx,reject,inputRaw:'30000000',expectedRaw:s.q.amountOut.amount.toString(),minOutRaw:s.min.toString(),actualRaw:String(after[1]-before[1]),beforePrice:s.price,afterPrice:String(end.poolInfo.price)};save();
}
if(process.argv.includes('--week12'))process.exit(0);

const otherPath=process.env.ANCHOR_WALLET+'.trader';
if(!existsSync(otherPath))writeFileSync(otherPath,JSON.stringify([...Keypair.generate().secretKey]),{flag:'wx',mode:0o600});
const trader=key(otherPath);
const ta=(await getOrCreateAssociatedTokenAccount(c,w,A,trader.publicKey)).address;
const tb=(await getOrCreateAssociatedTokenAccount(c,w,B,trader.publicKey)).address;
if((await getAccount(c,ta)).amount<1_000_000_000n)await send([createTransferInstruction(userA,ta,w.publicKey,1_600_000_000n)]);
if(!evidence.unauthorized){const s=await swap(true,1_000_000);evidence.unauthorized=await send([s.build(s.min,trader.publicKey)],[trader],/ConstraintHasOne/);save();}
const pick=async(width)=>{const {computePoolInfo:p}=await live();const center=Math.floor(p.tickCurrent/60)*60;return [center-width,center+width];};
async function positionParts(nft,lower,upper){
 const {computePoolInfo:p}=await live();
 const ls=TickUtils.getTickArrayStartIndexByTick(lower,60),us=TickUtils.getTickArrayStartIndexByTick(upper,60);
 const lt=getPdaTickArrayAddress(R,P,ls).publicKey,ut=getPdaTickArrayAddress(R,P,us).publicKey;
 const protocol=getPdaProtocolPositionAddress(R,P,lower,upper).publicKey, personal=getPdaPersonalPositionAddress(R,nft).publicKey;
 const nftAccount=getAssociatedTokenAddressSync(nft,state,true,TOKEN_2022_PROGRAM_ID);
 return {p,ls,us,lt,ut,protocol,personal,nftAccount};
}
async function open(width){
 const [lower,upper]=await pick(width);const nft=Keypair.generate();
 const {p,ls,us,lt,ut,protocol,personal,nftAccount}=await positionParts(nft.publicKey,lower,upper);
 const liquidity=new BN(250_000_000),cap=new BN(25_000_000);
 const rx=ClmmInstrument.openPositionFromLiquidityInstruction22(R,w.publicKey,P,state,nft.publicKey,nftAccount,protocol,lt,ut,personal,base,quote,p.vaultA,p.vaultB,A,B,lower,upper,ls,us,liquidity,cap,cap,'no-create');
 const before=await balance();const tx=await send([strategy('open_position',rx,w.publicKey,i(lower),i(upper),i(ls),i(us),u(liquidity,16),u(cap,8),u(cap,8))],[nft]);
 const account=await getAccount(c,nftAccount,'finalized',TOKEN_2022_PROGRAM_ID);assert.ok(account.owner.equals(state));assert.equal(account.amount,1n);
 for(const token of [base,quote]){
  const vaultToken=await getAccount(c,token,'finalized');
  assert.ok(vaultToken.owner.equals(state));
  assert.equal(vaultToken.delegate,null,'Opening left a token delegate on the vault');
  assert.equal(vaultToken.delegatedAmount,0n);
 }
 const info=PositionInfoLayout.decode((await c.getAccountInfo(personal)).data);assert.equal(info.liquidity.toString(),liquidity.toString());
 const after=await balance();return {tx,lower,upper,nft:String(nft.publicKey),personal:String(personal),liquidity:liquidity.toString(),depositedRaw:before.map((v,j)=>String(v-after[j]))};
}
async function unwind(rec,collect){
 const nft=new PublicKey(rec.nft);
 const {p,lt,ut,protocol,personal,nftAccount}=await positionParts(nft,rec.lower,rec.upper);
 const liq=new BN(collect?0:rec.liquidity);
 const minA=new BN(collect?0:1),minB=new BN(!collect&&p.tickCurrent>rec.lower?1:0);
 if(!collect&&p.tickCurrent>=rec.upper){minA.isubn(1);minB.iaddn(1);}
 const rx=ClmmInstrument.decreaseLiquidityInstruction(R,state,nftAccount,personal,P,protocol,lt,ut,base,quote,p.vaultA,p.vaultB,A,B,[],liq,minA,minB);
 const close=ClmmInstrument.closePositionInstruction(R,state,nft,nftAccount,personal,true);
 const before=await balance();
 const tx=await send(collect?[strategy('collect_fees',rx)]:[strategy('remove_liquidity',rx,w.publicKey,u(liq,16),u(minA,8),u(minB,8)),strategy('close_position',close)]);
 const after=await balance();const returnedRaw=after.map((v,j)=>String(v-before[j]));
 if(!collect)assert.deepEqual(await c.getMultipleAccountsInfo([personal,nft,nftAccount],'finalized'),[null,null,null]);
 else assert.ok(after.some((v,j)=>v>before[j]),'No fees collected');
 return {tx,returnedRaw,minRaw:[minA.toString(),minB.toString()]};
}
if(!evidence.position){evidence.position=await open(600);save();}
if(!evidence.trades){
 evidence.trades=[];
 for(const [aToB,n] of [[true,20_000_000],[false,10_000_000],[true,15_000_000]]){
  const s=await swap(aToB,n,trader,[ta,tb]); evidence.trades.push(await send([s.ix(s.min,trader.publicKey)],[trader]));
 }save();
}
if(!evidence.fees){evidence.fees=await unwind(evidence.position,true);save();}
if(!evidence.closed){evidence.closed=await unwind(evidence.position,false);save();}
if(!evidence.rebalanceOld){evidence.rebalanceOld=await open(120);save();}
if(!evidence.move){
 const s=await swap(true,200_000_000,trader,[ta,tb]); const tx=await send([s.ix(s.min,trader.publicKey)],[trader]);
 const {computePoolInfo:p}=await live();assert.ok(p.tickCurrent<evidence.rebalanceOld.lower,`tick ${p.tickCurrent} still in range`);
 evidence.move={tx,tick:p.tickCurrent};save();
}
if(!evidence.rebalanceClose){evidence.rebalanceClose=await unwind(evidence.rebalanceOld,false);save();}
if(!evidence.rebalanceNew){evidence.rebalanceNew=await open(600);assert.ok(evidence.move.tick>=evidence.rebalanceNew.lower&&evidence.move.tick<evidence.rebalanceNew.upper);save();}
console.log('Devnet evidence saved:',outPath.pathname);
