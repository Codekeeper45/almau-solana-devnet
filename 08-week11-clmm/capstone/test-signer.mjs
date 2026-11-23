// Local Devnet E2E only. This file never runs in the web app.
import { Keypair, VersionedTransaction } from '@solana/web3.js';
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const walletPath = process.env.ANCHOR_WALLET;
  if (!walletPath) throw new Error('Set ANCHOR_WALLET to a Devnet keypair JSON path');
  const signer = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(readFileSync(walletPath, 'utf8'))));
  if (process.argv[2] === 'pubkey') console.log(signer.publicKey.toBase58());
  else {
    const tx = VersionedTransaction.deserialize(Buffer.from(readFileSync(0, 'utf8').trim(), 'base64'));
    tx.sign([signer]);
    process.stdout.write(Buffer.from(tx.serialize()).toString('base64'));
  }
}
