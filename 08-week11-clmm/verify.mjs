import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { Connection, PublicKey } from '@solana/web3.js';
import { getMint, getAssociatedTokenAddressSync, getAccount } from '@solana/spl-token';
import { PoolInfoLayout, ClmmConfigLayout, PositionInfoLayout, DEVNET_PROGRAM_ID } from '@raydium-io/raydium-sdk-v2';
import { assertDevnet } from './create-pool.mjs';

const e = JSON.parse(readFileSync(process.argv[2] || 'evidence/devnet-pool.json', 'utf8'));
const rpc = new Connection(process.env.DEVNET_RPC || 'https://api.devnet.solana.com', 'finalized');
await assertDevnet(rpc);
assert.equal(e.cluster, 'devnet');
const program = DEVNET_PROGRAM_ID.CLMM_PROGRAM_ID;
assert.equal(e.clmmProgram, program.toBase58());
const wallet = new PublicKey(e.wallet);
const txOptions = { commitment: 'finalized', maxSupportedTransactionVersion: 0 };
const [pool, config, poolTx, mintTx] = await Promise.all([
  rpc.getAccountInfo(new PublicKey(e.poolId)), rpc.getAccountInfo(new PublicKey(e.ammConfig)),
  rpc.getTransaction(e.tx, txOptions), rpc.getTransaction(e.mintTx, txOptions),
]);
assert.ok(pool?.owner.equals(program));
assert.ok(config?.owner.equals(program));
assert.ok(poolTx?.meta && mintTx?.meta);
assert.equal(poolTx.meta.err, null);
assert.equal(mintTx.meta.err, null);
const keys = poolTx.transaction.message.staticAccountKeys.map(k => k.toBase58());
assert.ok(keys.includes(e.poolId) && keys.includes(e.clmmProgram));
const state = PoolInfoLayout.decode(pool.data);
const fees = ClmmConfigLayout.decode(config.data);
assert.deepEqual([state.mintA.toBase58(), state.mintB.toBase58()].sort(), [e.tokenA, e.tokenB].sort());
assert.equal(state.creator.toBase58(), e.wallet);
assert.equal(state.ammConfig.toBase58(), e.ammConfig);
assert.equal(state.tickSpacing, 60);
assert.equal(fees.tickSpacing, 60);
assert.equal(fees.tradeFeeRate, 2500);
assert.ok(BigInt(state.sqrtPriceX64.toString()) > 0n);
assert.ok(BigInt(state.liquidity.toString()) > 0n);
for (const address of [e.tokenA, e.tokenB]) {
  const mint = new PublicKey(address);
  const [info, ata] = await Promise.all([getMint(rpc, mint), getAccount(rpc, getAssociatedTokenAddressSync(mint, wallet))]);
  assert.ok(info.mintAuthority.equals(wallet));
  assert.equal(info.decimals, 6);
  assert.equal(info.supply, 1_000_000_000_000n);
  assert.ok(ata.amount > 0n);
}

let seedPosition = null;
const seedPath = 'evidence/devnet-seed-position.json';
if (!process.argv[2] && existsSync(seedPath)) {
  const s = JSON.parse(readFileSync(seedPath, 'utf8'));
  assert.equal(s.poolId, e.poolId);
  assert.equal(s.owner, e.wallet);
  assert.equal(s.tickLower, -1020);
  assert.equal(s.tickUpper, 960);
  const [posInfo, posTx] = await Promise.all([
    rpc.getAccountInfo(new PublicKey(s.position)),
    rpc.getTransaction(s.tx, txOptions),
  ]);
  assert.ok(posInfo?.owner.equals(program));
  assert.ok(posTx?.meta);
  assert.equal(posTx.meta.err, null);
  const decodedPos = PositionInfoLayout.decode(posInfo.data);
  assert.equal(decodedPos.poolId.toBase58(), e.poolId);
  assert.equal(decodedPos.nftMint.toBase58(), s.nftMint);
  assert.equal(decodedPos.tickLower, s.tickLower);
  assert.equal(decodedPos.tickUpper, s.tickUpper);
  assert.ok(BigInt(decodedPos.liquidity.toString()) > 0n);
  seedPosition = s.position;
}

console.log(JSON.stringify({
  finalized: true,
  pool: e.poolId,
  poolSlot: poolTx.slot,
  mintSlot: mintTx.slot,
  seedPosition,
  tickCurrent: state.tickCurrent,
  liquidity: state.liquidity.toString(),
  tickSpacing: state.tickSpacing,
  tradeFeeRate: fees.tradeFeeRate,
  initialPrice: 1,
}, null, 2));
