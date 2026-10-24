# Week 7: SPL Token + on-chain metadata (Devnet only)

This is a fresh-mint exercise. It deliberately does **not** alter the old mint `HzQULeq72G2RQp1wFBk9T3TNvCZ6wBBP3KrqQZVYxgfe`: its authority's private key is not present in the checked local secret files. The syllabus asks for token creation, minting, transfer, metadata, and client interaction; this exercise focuses on mint + minting + Metaplex Token Metadata PDA. Add a transfer/client demonstration after creation if required for the class evidence.

## Safety

- The script hardcodes `https://api.devnet.solana.com`; there is no mainnet flag or endpoint override.
- Devnet SOL is valueless test SOL. No purchases, paid upload services, or mainnet transactions.
- Use the existing student payer only after faucet funding. New mint signer is stored outside Git at `~/.hermes/secrets/almau-solana-week7/week7-mint.json`, mode 0600.
- The metadata JSON can be hosted as a public raw file in the educational GitHub repository. No push was performed. Its HTTPS URL is needed on the Metaplex account; this rehearsal cannot complete until the file is hosted and the payer funded.

## Steps

1. Ensure `/home/hermes/.hermes/secrets/almau-solana-devnet.json` contains the existing Devnet payer and is chmod 600. Never print or commit it.
2. Upload `metadata.json` to the intended educational GitHub repository without changing branches or pushing without approval. Use the resulting public HTTPS raw URL (not a `github.com/.../blob/...` HTML page).
3. From this folder, run:

   ```bash
   /home/hermes/projects/almau-moodle/tasks/audit-2026-10-24/.venv/bin/python week7_metadata.py \
     --metadata-uri 'https://raw.githubusercontent.com/OWNER/REPO/BRANCH/06-week7-metadata/metadata.json'
   ```

   The script aborts if payer balance is below 0.01 SOL. If a transaction succeeds it waits for confirmation, fetches each transaction from RPC, then checks that the metadata PDA exists and is owned by the Metaplex Token Metadata program. Output/evidence is written only after these checks.
4. Verify mint and metadata account in Solana Explorer with the Devnet cluster selector. Preserve the printed signatures and `evidence/week7-devnet.json`; do not claim completion unless RPC verification succeeded.

## Local checks

```bash
/home/hermes/projects/almau-moodle/tasks/audit-2026-10-24/.venv/bin/python -m py_compile week7_metadata.py
/home/hermes/projects/almau-moodle/tasks/audit-2026-10-24/.venv/bin/python week7_metadata.py --help
```

No metadata PDA or mint was created during preparation: the payer has zero balance and no public metadata URI has been provisioned. The script uses classic SPL Token plus the Metaplex Token Metadata program, so the name/symbol/URI are stored in a real on-chain metadata account rather than inferred from a local JSON file.

## Implementation caveat

This is minimal direct instruction construction with `solders`/`requests`, not an installed Metaplex SDK. Before funded use, execute once on Devnet, inspect the returned RPC transaction and PDA, and correct any RPC/Metaplex program-version incompatibility before treating it as complete. Failed preflight or account verification must be reported as a blocker, not as a successful mint.
