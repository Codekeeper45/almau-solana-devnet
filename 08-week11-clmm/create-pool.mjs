import { readFileSync, existsSync, writeFileSync } from 'node:fs';
import { Connection, Keypair, PublicKey, SystemProgram, Transaction, sendAndConfirmTransaction } from '@solana/web3.js';
import { TOKEN_PROGRAM_ID, MINT_SIZE, createInitializeMint2Instruction, createAssociatedTokenAccountInstruction, createMintToInstruction, getAssociatedTokenAddressSync } from '@solana/spl-token';
import { Raydium, DEVNET_PROGRAM_ID, DEV_API_URLS, TxVersion } from '@raydium-io/raydium-sdk-v2';
import Decimal from 'decimal.js';

export const DEVNET_GENESIS = 'EtWTRABZaYq6iMfeYKouRu166VU2xqa1wcaWoxPkrZBG';
const programId = DEVNET_PROGRAM_ID.CLMM_PROGRAM_ID;
const decimals = 6;
const rawAmount = 1_000_000_000_000n;
const rpc = process.env.DEVNET_RPC || 'https://api.devnet.solana.com';

export async function assertDevnet(connection) {
  if (await connection.getGenesisHash() !== DEVNET_GENESIS) throw new Error('Допускается только Solana Devnet');
}

async function main() {
  const connection = new Connection(rpc, 'finalized');
  await assertDevnet(connection);
  const wallet = process.env.ANCHOR_WALLET;
  if (!wallet) throw new Error('Укажи ANCHOR_WALLET с тестовым кошельком');
  const file = 'devnet-pool.json';
  if (existsSync(file)) throw new Error('Пул уже записан; повторный запуск отключён');
  const owner = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(readFileSync(wallet, 'utf8'))));
  const balance = await connection.getBalance(owner.publicKey);
  if (balance < 1_000_000_000) throw new Error(`Нужно от 1 тестового SOL, баланс ${balance} lamports`);

  const raydium = await Raydium.load({ owner, connection, cluster: 'devnet', disableFeatureCheck: true, disableLoadToken: true, blockhashCommitment: 'finalized', urlConfigs: DEV_API_URLS });
  const candidates = (await raydium.api.getClmmConfigs()).filter(c => c.tickSpacing === 60 && c.tradeFeeRate === 2500);
  let config;
  for (const candidate of candidates) {
    const info = await connection.getAccountInfo(new PublicKey(candidate.id));
    if (info?.owner.equals(programId)) { config = candidate; break; }
  }
  if (!config) throw new Error('Не найден подтверждённый конфиг Devnet: шаг 60, комиссия 0,25%');

  // Один атомарный перевод: обе mint и оба счёта либо созданы, либо не созданы вовсе.
  const checkpoint = '.devnet-mints.json';
  let mintRecord;
  if (existsSync(checkpoint)) {
    mintRecord = JSON.parse(readFileSync(checkpoint, 'utf8'));
    if (mintRecord.wallet !== owner.publicKey.toBase58()) throw new Error('Кошелёк не совпадает с первой транзакцией');
  } else {
    const signers = [Keypair.generate(), Keypair.generate()];
    const tx = new Transaction();
    const rent = await connection.getMinimumBalanceForRentExemption(MINT_SIZE);
    for (const { publicKey: mint } of signers) {
      const ata = getAssociatedTokenAddressSync(mint, owner.publicKey);
      tx.add(SystemProgram.createAccount({ fromPubkey: owner.publicKey, newAccountPubkey: mint, space: MINT_SIZE, lamports: rent, programId: TOKEN_PROGRAM_ID }), createInitializeMint2Instruction(mint, decimals, owner.publicKey, null), createAssociatedTokenAccountInstruction(owner.publicKey, ata, owner.publicKey, mint), createMintToInstruction(mint, ata, owner.publicKey, rawAmount));
    }
    const mintTx = await sendAndConfirmTransaction(connection, tx, [owner, ...signers], { commitment: 'finalized' });
    mintRecord = { wallet: owner.publicKey.toBase58(), tokenA: signers[0].publicKey.toBase58(), tokenB: signers[1].publicKey.toBase58(), mintTx };
    writeFileSync(checkpoint, JSON.stringify(mintRecord, null, 2) + '\n', { flag: 'wx' });
  }

  const token = address => ({ address, programId: TOKEN_PROGRAM_ID.toBase58(), decimals });
  const { execute, extInfo } = await raydium.clmm.createPool({ programId, mint1: token(mintRecord.tokenA), mint2: token(mintRecord.tokenB), ammConfig: { ...config, id: new PublicKey(config.id), fundOwner: '', description: '' }, initialPrice: new Decimal(1), txVersion: TxVersion.V0 });
  const { txId } = await execute({ sendAndConfirm: true });
  const evidence = { cluster: 'devnet', ...mintRecord, poolId: String(extInfo.address.id), clmmProgram: programId.toBase58(), ammConfig: config.id, tickSpacing: 60, tradeFeeRate: 2500, initialPrice: 1, tx: txId };
  writeFileSync(file, JSON.stringify(evidence, null, 2) + '\n', { flag: 'wx' });
  console.log(JSON.stringify(evidence, null, 2));
}

if (process.argv[1] && import.meta.url === new URL(process.argv[1], 'file://').href) main().catch(error => { console.error(error); process.exitCode = 1; });
