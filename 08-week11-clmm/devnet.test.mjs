import assert from 'node:assert/strict';
import test from 'node:test';
import {assertDevnet, DEVNET_GENESIS} from './create-pool.mjs';

test('accepts devnet', () => assertDevnet({getGenesisHash: async () => DEVNET_GENESIS}));
test('rejects mainnet before any transaction', () => assert.rejects(assertDevnet({getGenesisHash: async () => '5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp'}), /только Solana Devnet/));
