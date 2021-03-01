import pytest


@pytest.fixture()
# This set of wallet words corresponds to a 256-bit entropy value with all zeros
def zero_wallet_words():
    return "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon art"


@pytest.fixture()
def zero_bytes():
    return b"\x00" * 32


@pytest.fixture()
def unencrypted_mnemonic_1():
    return "crucial extend category march apart overall expect wrap teaspoon rich finance hazard lunch painting domain fortune hand bracelet ruler humidity painting exercise necklace ordinary wildlife family quiet findings luck founder kidney flip champion"


@pytest.fixture()
def encrypted_mnemonic_1():
    return "crucial extend category march apart express scholar strike cards evening laden domain firm program aunt founder prize firm glimpse swimming fishing easel explain document stay injury charity step lobe both theory alto knit"


@pytest.fixture()
def password_1():
    return b"password"


@pytest.fixture()
def password_2():
    return b"drowssap"


@pytest.fixture()
def shamir_mnemonic_2_of_2():
    return [
        [
            "dismiss stay academic acid afraid lift aspect hanger armed intimate rumor depend grill curly class antenna username twice rhythm credit require thumb family surface lying cricket wolf lamp album license enforce true hunting",
            "dismiss stay academic agency august mandate space recover argue miracle ambition tension home arena marvel document move simple stick friendly fiber grief envelope blessing wits width elevator taught terminal focus false thumb hesitate",
        ]
    ]


@pytest.fixture()
def shamir_2_of_2_secret():
    return b'\x8e\xd03D\xee1"\xc3Jec\xc9\xf7zd\x80t\x08\xae?\x8c\x98\xe0\x16{|\xc3\xe0\x97\xf3\x9e\xc4'
