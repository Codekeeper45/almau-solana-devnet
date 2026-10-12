import hashlib, json, struct
from pathlib import Path
from solders.pubkey import Pubkey

COUNTER_PROGRAM = Pubkey.from_string("Fg6PaFpoGXkYsidMpWxTWqkZ8q7kL6K2f3d9c8P4v1A")
PROFILE_PROGRAM = Pubkey.from_string("Fg6PaFpoGXkYsidMpWxTWqkZ8q7kL6K2f3d9c8P4v1B")
STUDENT_AUTHORITY = Pubkey.from_string("2SzJ2PSuhnQsenfvHK4DhQHibjVL2d68fwdHAMwxJ7pL")

def discriminator(namespace: str, name: str) -> bytes:
    return hashlib.sha256(f"{namespace}:{name}".encode()).digest()[:8]

def borsh_string(text: str) -> bytes:
    raw = text.encode("utf-8")
    return struct.pack("<I", len(raw)) + raw

def read_borsh_string(buf: bytes, offset: int) -> tuple[str, int]:
    (length,) = struct.unpack_from("<I", buf, offset)
    offset += 4
    return buf[offset:offset + length].decode("utf-8"), offset + length

def encode_counter_instruction(name: str) -> bytes:
    assert name in {"initialize", "increment", "decrement"}
    return discriminator("global", name)

def encode_counter_account(authority: Pubkey, count: int) -> bytes:
    return discriminator("account", "Counter") + bytes(authority) + struct.pack("<Q", count)

def decode_counter_account(data: bytes) -> dict:
    assert data[:8] == discriminator("account", "Counter")
    authority = Pubkey.from_bytes(data[8:40])
    (count,) = struct.unpack_from("<Q", data, 40)
    return {"authority": str(authority), "count": count}

def derive_profile_pda(authority: Pubkey, program_id: Pubkey = PROFILE_PROGRAM) -> tuple[Pubkey, int]:
    return Pubkey.find_program_address([b"profile", bytes(authority)], program_id)

def encode_profile_instruction(name: str, username: str, bio: str) -> bytes:
    assert name in {"create_profile", "update_profile"}
    assert len(username.encode("utf-8")) <= 32
    assert len(bio.encode("utf-8")) <= 160
    return discriminator("global", name) + borsh_string(username) + borsh_string(bio)

def encode_profile_account(authority: Pubkey, username: str, bio: str, bump: int) -> bytes:
    return discriminator("account", "UserProfile") + bytes(authority) + borsh_string(username) + borsh_string(bio) + struct.pack("<B", bump)

def decode_profile_account(data: bytes) -> dict:
    assert data[:8] == discriminator("account", "UserProfile")
    authority = Pubkey.from_bytes(data[8:40])
    username, off = read_borsh_string(data, 40)
    bio, off = read_borsh_string(data, off)
    (bump,) = struct.unpack_from("<B", data, off)
    return {"authority": str(authority), "username": username, "bio": bio, "bump": bump}

if __name__ == "__main__":
    pda, bump = derive_profile_pda(STUDENT_AUTHORITY)
    recreated = Pubkey.create_program_address([b"profile", bytes(STUDENT_AUTHORITY), bytes([bump])], PROFILE_PROGRAM)
    assert pda == recreated
    counter_raw = encode_counter_account(STUDENT_AUTHORITY, 2)
    assert decode_counter_account(counter_raw) == {"authority": str(STUDENT_AUTHORITY), "count": 2}
    profile_raw = encode_profile_account(STUDENT_AUTHORITY, "emir_ds", "AlmaU 3 course", bump)
    assert decode_profile_account(profile_raw) == {"authority": str(STUDENT_AUTHORITY), "username": "emir_ds", "bio": "AlmaU 3 course", "bump": bump}
    summary = {
        "mode": "local_client_and_unit_tests_only",
        "student_authority": str(STUDENT_AUTHORITY),
        "counter_program_id": str(COUNTER_PROGRAM),
        "counter_increment_discriminator_hex": encode_counter_instruction("increment").hex(),
        "profile_program_id": str(PROFILE_PROGRAM),
        "derived_profile_pda": str(pda),
        "derived_profile_bump": bump,
        "create_profile_instruction_hex": encode_profile_instruction("create_profile", "emir_ds", "AlmaU 3 course").hex(),
    }
    out = Path(__file__).resolve().parent.parent / "evidence" / "w4-w6" / "client_verification.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
