import './polyfill.mjs';
import {Buffer} from 'buffer';
import {Connection,Keypair,PublicKey,ComputeBudgetProgram,SystemProgram,TransactionInstruction,TransactionMessage,VersionedTransaction} from '@solana/web3.js';
import {getAssociatedTokenAddressSync,TOKEN_PROGRAM_ID,TOKEN_2022_PROGRAM_ID,createAssociatedTokenAccountIdempotentInstruction} from '@solana/spl-token';
import {ClmmInstrument,Raydium,DEV_API_URLS,PoolUtils,PositionInfoLayout,TickUtils,SqrtPriceMath,LiquidityMath,getPdaPersonalPositionAddress,getPdaProtocolPositionAddress,getPdaTickArrayAddress} from '@raydium-io/raydium-sdk-v2';
import BN from 'bn.js';
import pool from '../evidence/devnet-pool.json';
import deployment from '../evidence/devnet-weeks12-13.json';

const genesis='EtWTRABZaYq6iMfeYKouRu166VU2xqa1wcaWoxPkrZBG';
const conn=new Connection('https://api.devnet.solana.com','confirmed');
const pk=x=>new PublicKey(x);
const [program,state,P,R,A,B,C]=[deployment.program,deployment.vault,pool.poolId,pool.clmmProgram,pool.tokenA,pool.tokenB,pool.ammConfig].map(pk);
const pda=(seed,...xs)=>PublicKey.findProgramAddressSync([Buffer.from(seed),...xs.map(x=>x.toBuffer())],program)[0];
const base=pda('vault_tokens',A), share=pda('share_mint',A), quote=getAssociatedTokenAddressSync(B,state,true);
const $=id=>document.getElementById(id);
const key=(pubkey,isWritable=false,isSigner=false)=>({pubkey,isWritable,isSigner});
const u=(x,n)=>new BN(String(x)).toArrayLike(Buffer,'le',n);
const i32=x=>{const b=Buffer.alloc(4);b.writeInt32LE(x);return b;};
const amount=(s,d=6)=>{if(!/^\d+(\.\d{1,6})?$/.test(s))throw new Error('Введите положительное число, до 6 знаков после точки'); const [a,b='']=s.split('.'); const n=BigInt(a)*10n**BigInt(d)+BigInt(b.padEnd(d,'0')); if(n<=0n||n>=2n**64n)throw new Error('Сумма вне диапазона'); return n;};
const pretty=n=>`${n/1000000n}.${String(n%1000000n).padStart(6,'0')}`;
const address=()=>wallet?.publicKey?pk(wallet.publicKey.toString()):null;
let wallet, busy=false, signature=null;
async function own(name,keys,...body){const h=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(`global:${name}`));return new TransactionInstruction({programId:program,keys,data:Buffer.concat([Buffer.from(h).subarray(0,8),...body])});}
const strategy=(name,rx,...body)=>own(name,[key(address(),false,true),key(state,true),key(base,true),key(quote,true),key(R),...rx.keys.map(k=>k.pubkey.equals(state)?{...k,isSigner:false}:k)],...body);
async function network(){if(await conn.getGenesisHash()!==genesis)throw new Error('RPC не Solana Devnet');}
async function vault(){const x=await conn.getAccountInfo(state);if(!x?.owner.equals(program)||x.data.length<193)throw new Error('Хранилище не найдено'); const b=Buffer.from(x.data);return {admin:pk(b.subarray(8,40)),shares:b.readBigUInt64LE(144),position:pk(b.subarray(153,185)),quote:b.readBigUInt64LE(185)};}
const raw=x=>x?Buffer.from(x.data).readBigUInt64LE(64):0n;
const posActive=v=>!v.position.equals(PublicKey.default);
async function refresh(){
 const v=await vault(), user=address(); const addresses=[base,quote]; if(user)addresses.push(getAssociatedTokenAddressSync(A,user),getAssociatedTokenAddressSync(share,user));
 const [ba,qu,a,sh]=await conn.getMultipleAccountsInfo(addresses);
 $('balances').textContent=`В хранилище: ${pretty(raw(ba))} A, ${pretty(raw(qu))} B. Выпущено долей: ${pretty(v.shares)}.`+(user?` У вас: ${pretty(raw(a))} A и ${pretty(raw(sh))} долей.`:'');
 $('state').textContent=posActive(v)?`Позиция открыта: ${v.position}`:v.quote?'Сначала обменяйте B обратно в A.':'Позиция закрыта, вклад и вывод доступны.';
 $('wallet').textContent=user?`Кошелёк: ${user}`:'Кошелёк не подключён'; $('admin').hidden=!user?.equals(v.admin);
}
async function send(ixs,signers){
 const payer=address(); const block=await conn.getLatestBlockhash();
 const tx=new VersionedTransaction(new TransactionMessage({payerKey:payer,recentBlockhash:block.blockhash,instructions:[ComputeBudgetProgram.setComputeUnitLimit({units:950000}),...ixs]}).compileToV0Message());
 const signed=await wallet.signTransaction(tx);
 if(signers.length)signed.sign(signers);
 if(!address()?.equals(payer))throw new Error('Кошелёк сменился');
 const id=await conn.sendRawTransaction(signed.serialize(),{maxRetries:3}); signature=id; show('Отправлено, ожидаю подтверждение',id);
 const result=await conn.confirmTransaction({...block,signature:id},'confirmed'); if(result.value.err)throw new Error('Сеть отклонила транзакцию'); show('Подтверждено',id);
}
function show(text,id){const o=$('status');o.textContent=text;if(id){const a=document.createElement('a');a.textContent=' Открыть в Explorer';a.href=`https://explorer.solana.com/tx/${id}?cluster=devnet`;a.target='_blank';a.rel='noopener noreferrer';o.append(a);}}
async function userAction(name,v,user){
 if(posActive(v)||v.quote!==0n)throw new Error('Сначала администратор должен закрыть позицию и обменять B на A');
 const n=amount($('amount').value.trim()), card=pda('user_card',state,user), ua=getAssociatedTokenAddressSync(A,user), us=getAssociatedTokenAddressSync(share,user);
 const [ca,ta,sa]=await conn.getMultipleAccountsInfo([card,ua,us]);
 if(name==='deposit'&&raw(ta)<n)throw new Error('Недостаточно токена A'); if(name==='withdraw'&&(!ca||raw(sa)<n))throw new Error('Недостаточно долей');
 const xs=[]; if(!ca)xs.push(await own('create_user_card',[key(state),key(card,true),key(user,true,true),key(SystemProgram.programId)]));
 if(!sa)xs.push(createAssociatedTokenAccountIdempotentInstruction(user,us,user,share));
 if(!ta)xs.push(createAssociatedTokenAccountIdempotentInstruction(user,ua,user,A));
 xs.push(await own(name,[key(state,true),key(card,true),key(base,true),key(share,true),key(ua,true),key(us,true),key(user,true,true),key(TOKEN_PROGRAM_ID)],u(n,8)));
 await send(xs,[]);
}
async function adminAction(name,v,user){
 if(!user.equals(v.admin))throw new Error('Нужен кошелёк администратора');
 const sdk=await Raydium.load({connection:conn,owner:user,cluster:'devnet',urlConfigs:DEV_API_URLS,disableFeatureCheck:true,disableLoadToken:true});
 const {computePoolInfo:p,tickData}=await sdk.clmm.getPoolInfoFromRpc(pool.poolId);
 if(name==='swap'){
   const forward=$('direction').value==='ab', n=new BN(String(amount($('swapAmount').value.trim())));
   const mint=forward?A:B;
   const q=PoolUtils.computeAmountOut({poolInfo:p,tickArrayCache:tickData[pool.poolId],baseMint:mint,epochInfo:await conn.getEpochInfo(),amountIn:n,slippage:0.01,catchLiquidityInsufficient:false});
   const min=q.minAmountOut.amount;if(min.isZero())throw new Error('Сумма слишком мала для обмена');
   const rx=ClmmInstrument.swapInstruction(R,state,P,C,forward?base:quote,forward?quote:base,forward?p.vaultA:p.vaultB,forward?p.vaultB:p.vaultA,mint,forward?B:A,q.remainingAccounts,p.observationId,n,min,new BN(0),true);
   return send([await strategy('swap',rx,u(n,8),u(min,8),Buffer.from([+forward]))],[]);
 }
 const parts=(nft,lower,upper)=>{const ls=TickUtils.getTickArrayStartIndexByTick(lower,60),us=TickUtils.getTickArrayStartIndexByTick(upper,60);return {ls,us,lt:getPdaTickArrayAddress(R,P,ls).publicKey,ut:getPdaTickArrayAddress(R,P,us).publicKey,proto:getPdaProtocolPositionAddress(R,P,lower,upper).publicKey,personal:getPdaPersonalPositionAddress(R,nft).publicKey,ata:getAssociatedTokenAddressSync(nft,state,true,TOKEN_2022_PROGRAM_ID)};};
 if(name==='open'){
   if(posActive(v))throw new Error('Уже есть открытая позиция'); const width=Number($('width').value), text=$('liquidity').value;
   if(!Number.isSafeInteger(width)||width<60||width>10000||width%60||!/^\d{1,38}$/.test(text)||BigInt(text)<=0n)throw new Error('Проверьте ликвидность и диапазон');
   const n=new BN(text), limit=new BN(String(amount($('cap').value.trim()))), nft=Keypair.generate(); const center=Math.floor(p.tickCurrent/60)*60, lower=center-width,upper=center+width;
   const {ls,us,lt,ut,proto,personal,ata}=parts(nft.publicKey,lower,upper);
   const rx=ClmmInstrument.openPositionFromLiquidityInstruction22(R,user,P,state,nft.publicKey,ata,proto,lt,ut,personal,base,quote,p.vaultA,p.vaultB,A,B,lower,upper,ls,us,n,limit,limit,'no-create');
   return send([await strategy('open_position',rx,i32(lower),i32(upper),i32(ls),i32(us),u(n,16),u(limit,8),u(limit,8))],[nft]);
 }
 if(!posActive(v))throw new Error('Нет открытой позиции'); const info=await conn.getAccountInfo(v.position); if(!info?.owner.equals(R))throw new Error('Позиция в Raydium не найдена');
 const {nftMint,tickLower,tickUpper,liquidity}=PositionInfoLayout.decode(info.data);
 const {lt,ut,proto,personal,ata}=parts(nftMint,tickLower,tickUpper);
 if(!personal.equals(v.position))throw new Error('Некорректный адрес позиции');
 const collect=name==='fees', liq=collect?new BN(0):liquidity;
 const mins=collect?{amountSlippageA:new BN(0),amountSlippageB:new BN(0)}:LiquidityMath.getAmountsFromLiquidityWithSlippage(p.sqrtPriceX64,SqrtPriceMath.getSqrtPriceX64FromTick(tickLower),SqrtPriceMath.getSqrtPriceX64FromTick(tickUpper),liq,false,false,0.01);
 const {amountSlippageA:ma,amountSlippageB:mb}=mins;
 const rx=ClmmInstrument.decreaseLiquidityInstruction(R,state,ata,personal,P,proto,lt,ut,base,quote,p.vaultA,p.vaultB,A,B,[],liq,ma,mb);
 if(collect)return send([await strategy('collect_fees',rx)],[]);
 const close=ClmmInstrument.closePositionInstruction(R,state,nftMint,ata,personal,true);
 return send([await strategy('remove_liquidity',rx,u(liq,16),u(ma,8),u(mb,8)),await strategy('close_position',close)],[]);
}
async function run(fn){if(busy)return;busy=true;signature=null;for(const b of document.querySelectorAll('button'))b.disabled=true;try{await fn();}catch(e){show(e.message||String(e),signature);}finally{busy=false;for(const b of document.querySelectorAll('button'))b.disabled=false;}}
$('connect').onclick=()=>run(async()=>{wallet=window.phantom?.solana||window.solflare||(window.solana?.signTransaction?window.solana:null);if(!wallet?.connect||!wallet.signTransaction)throw new Error('Не найден Phantom или Solflare. Откройте страницу в браузере с расширением и выберите Devnet.');const res=await wallet.connect();if(!wallet.publicKey&&res?.publicKey)wallet.publicKey=res.publicKey;await refresh();show('Кошелёк подключён. Подписывайте только после проверки сети и суммы.');});
$('refresh').onclick=()=>run(refresh);
for(const b of document.querySelectorAll('[data-action]'))b.onclick=()=>run(async()=>{const user=address();if(!user)throw new Error('Сначала подключите кошелёк');await network();const v=await vault(),name=b.dataset.action;show('Подготовка транзакции');if(name==='deposit'||name==='withdraw')await userAction(name,v,user);else await adminAction(name,v,user);try{await refresh();}catch{show('Транзакция подтверждена, балансы можно обновить вручную',signature);}});
run(async()=>{await network();await refresh();});
