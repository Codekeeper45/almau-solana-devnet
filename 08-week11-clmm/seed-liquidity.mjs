import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import assert from 'node:assert/strict';
import { Connection, Keypair, PublicKey } from '@solana/web3.js';
import { getAccount, TOKEN_2022_PROGRAM_ID } from '@solana/spl-token';
import { Raydium, DEV_API_URLS, DEVNET_PROGRAM_ID, PositionInfoLayout, TxVersion } from '@raydium-io/raydium-sdk-v2';
import { assertDevnet } from './create-pool.mjs';
import BN from 'bn.js';

const file = 'evidence/devnet-seed-position.json';
const { poolId } = JSON.parse(readFileSync('evidence/devnet-pool.json', 'utf8'));
const connection = new Connection(process.env.DEVNET_RPC || 'https://api.devnet.solana.com', 'finalized');
await assertDevnet(connection);
const pool = new PublicKey(poolId);
const clmm = DEVNET_PROGRAM_ID.CLMM_PROGRAM_ID;
assert.ok((await connection.getAccountInfo(pool))?.owner.equals(clmm));
let evidence;
if (existsSync(file)) {
  evidence = JSON.parse(readFileSync(file, 'utf8'));
} else {
  const owner = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(readFileSync(process.env.ANCHOR_WALLET, 'utf8'))));
  const sdk = await Raydium.load({ connection, owner, cluster:'devnet', urlConfigs:DEV_API_URLS, disableFeatureCheck:true, disableLoadToken:true });
  const { poolInfo, poolKeys } = await sdk.clmm.getPoolInfoFromRpc(poolId);
  const tickLower = -1020, tickUpper = 960;
  assert.equal(poolInfo.config.tickSpacing, 60);
  const { execute, extInfo } = await sdk.clmm.openPositionFromLiquidity({ poolInfo, poolKeys, tickLower, tickUpper, liquidity: new BN(20_000_000_000), amountMaxA: new BN(1_100_000_000), amountMaxB: new BN(1_100_000_000), ownerInfo: {useSOLBalance:false}, nft2022: true, withMetadata:'no-create', txVersion:TxVersion.V0, computeBudgetConfig:{units:600000} });
  const {txId} = await execute({sendAndConfirm:true});
  const {nftMint, positionNftAccount, personalPosition} = extInfo.address;
  evidence = {poolId, tickLower, tickUpper, tx:txId, nftMint:String(nftMint), nftAccount:String(positionNftAccount), position:String(personalPosition), owner:String(owner.publicKey)};
  writeFileSync(file, JSON.stringify(evidence,null,2)+'\n',{flag:'wx'});
}
const info = await connection.getAccountInfo(new PublicKey(evidence.position));
assert.ok(info?.owner.equals(clmm));
const position = PositionInfoLayout.decode(info.data);
assert.equal(String(position.poolId), poolId);
assert.equal(String(position.nftMint), evidence.nftMint);
assert.equal(position.tickLower, evidence.tickLower);
assert.equal(position.tickUpper, evidence.tickUpper);
assert.ok(position.liquidity.gt(new BN(0)));
const nft = await getAccount(connection, new PublicKey(evidence.nftAccount), 'finalized', TOKEN_2022_PROGRAM_ID);
assert.equal(String(nft.owner), evidence.owner);
assert.equal(nft.amount, 1n);
const tx = await connection.getTransaction(evidence.tx,{commitment:'finalized',maxSupportedTransactionVersion:0});
assert.ok(tx?.meta);
assert.equal(tx.meta.err,null);
console.log({ ...evidence, liquidity:position.liquidity.toString(), slot:tx.slot });
