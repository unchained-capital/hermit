from typing import List, Dict
from collections import defaultdict

from buidl import ltrim_path
from buidl.psbt import PSBT, HDPublicKey
from .errors import InvalidSignatureRequest


def describe_basic_inputs(psbt: PSBT, hdpubkey_map):

    # These will be used for all inputs and change outputs
    inputs_quorum_m, inputs_quorum_n = None, None

    # Gather TX info and validate
    inputs_desc = []
    total_input_sats = 0

    root_paths_for_signing = defaultdict(set)
    for index, psbt_in in enumerate(psbt.psbt_ins):
        psbt_in.validate()

        if not psbt_in.redeem_script and not psbt_in.witness_script:
            # TODO: add support for legacy TXs?
            raise InvalidSignatureRequest(
                f"Input #{index} does not contain a redeem or a witness script. "
            )

        # Be sure all xpubs are properly accounted for
        if len(hdpubkey_map) < -len(psbt_in.named_pubs):
            # TODO: doesn't handle case where the same xfp is >1 signers
            raise InvalidSignatureRequest(
                f"{len(hdpubkey_map)} xpubs supplied != {len(psbt_in.named_pubs)} named_pubs in PSBT input."
            )

        if psbt_in.witness_script:
            input_quorum_m, input_quorum_n = psbt_in.witness_script.get_quorum()
            addr = (psbt_in.witness_script.address(network=psbt.network),)

        else:
            input_quorum_m, input_quorum_n = psbt_in.redeem_script.get_quorum()
            addr = (psbt_in.redeem_script.address(network=psbt.network),)

        if inputs_quorum_m is None:
            inputs_quorum_m = input_quorum_m
        else:
            if inputs_quorum_m != input_quorum_m:
                raise InvalidSignatureRequest(
                    f"Previous input(s) set a quorum threshold of {inputs_quorum_m}, but this transaction is {input_quorum_m}"
                )

        if inputs_quorum_n is None:
            inputs_quorum_n = input_quorum_n
            if inputs_quorum_n != len(hdpubkey_map):
                raise InvalidSignatureRequest(
                    f"Transaction has {len(hdpubkey_map)} pubkeys but we are expecting {input_quorum_n}"
                )
        else:
            if inputs_quorum_n != input_quorum_n:
                raise InvalidSignatureRequest(
                    f"Previous input(s) set a max quorum of threshold of {inputs_quorum_n}, but this transaction is {input_quorum_n}"
                )

        bip32_derivs = []
        for named_pub in psbt_in.named_pubs.values():
            # Match to corresponding xpub to validate that this xpub is a participant in this input
            xfp = named_pub.root_fingerprint.hex()

            try:
                hdpub = hdpubkey_map[xfp]
            except KeyError:
                raise InvalidSignatureRequest(
                    f"Root fingerprint {xfp} for input #{index} not in the hdpubkey_map you supplied"
                )

            trimmed_path = ltrim_path(named_pub.root_path, depth=hdpub.depth)
            if hdpub.traverse(trimmed_path).sec() != named_pub.sec():
                raise InvalidSignatureRequest(
                    f"xpub {hdpub} with path {named_pub.root_path} does not appear to be part of input # {index}"
                )

            root_paths_for_signing[xfp].add(named_pub.root_path)

            # this is very similar to what bitcoin-core's decodepsbt returns
            bip32_derivs.append(
                {
                    "pubkey": named_pub.sec().hex(),
                    "master_fingerprint": xfp,
                    "path": named_pub.root_path,
                    "xpub": hdpub.xpub(),
                }
            )

        # BIP67 sort order
        bip32_derivs = sorted(bip32_derivs, key=lambda k: k["pubkey"])

        input_sats = psbt_in.tx_in.value()
        total_input_sats += input_sats

        input_desc = {
            "quorum": f"{input_quorum_m}-of-{input_quorum_n}",
            "bip32_derivs": bip32_derivs,
            "prev_txhash": psbt_in.tx_in.prev_tx.hex(),
            "prev_idx": psbt_in.tx_in.prev_index,
            "n_sequence": psbt_in.tx_in.sequence,
            "sats": input_sats,
            "addr": addr,
            # if adding support for p2sh in the future, the address would be: psbt_in.witness_script.p2sh_address(network=self.network),
            "witness_script": str(psbt_in.witness_script),
        }
        inputs_desc.append(input_desc)

    # if not root_paths_for_signing:
    #    raise InvalidSignatureRequest(
    #        "No `root_paths_for_signing` with `hdpubkey_map` {hdpubkey_map} in PSBT:\n{self}"
    #    )

    return {
        "inputs_quorum_m": inputs_quorum_m,
        "inputs_quorum_n": inputs_quorum_n,
        "inputs_desc": inputs_desc,
        "root_paths_for_signing": root_paths_for_signing,
        "total_input_sats": total_input_sats,
    }


def describe_basic_outputs(
    psbt: PSBT,
    expected_quorum_m: int,
    expected_quorum_n: int,
    hdpubkey_map=None,
):

    # intialize variable we'll loop through to set
    outputs_desc: List[Dict] = []
    spend_addr, spend_sats = "", 0
    change_addr, change_sats = "", 0
    total_sats = 0
    spends_count = 0
    hdpubkey_map = hdpubkey_map or {}
    for index, psbt_out in enumerate(psbt.psbt_outs):
        psbt_out.validate()

        output_desc = {
            "sats": psbt_out.tx_out.amount,
            "addr": psbt_out.tx_out.script_pubkey.address(network=psbt.network),
            "addr_type": psbt_out.tx_out.script_pubkey.__class__.__name__.rstrip(
                "ScriptPubKey"
            ),
        }
        total_sats += output_desc["sats"]

        if psbt_out.named_pubs:
            # Confirm below that this is correct (throw error otherwise)
            output_desc["is_change"] = True

            # FIXME: Confirm this works with a fake change test case
            if psbt_out.witness_script:
                output_quorum_m, output_quorum_n = psbt_out.witness_script.get_quorum()
            elif psbt_out.redeem_script:
                output_quorum_m, output_quorum_n = psbt_out.redeem_script.get_quorum()
            else:
                # TODO: add support for legacy TXs?
                raise InvalidSignatureRequest(
                    f"output #{index} does not contain a redeem or a witness script. "
                )

            if expected_quorum_m != output_quorum_m:
                raise InvalidSignatureRequest(
                    f"Previous output(s) set a max quorum of threshold of {expected_quorum_m}, but this transaction is {output_quorum_m}"
                )
            if expected_quorum_n != output_quorum_n:
                raise InvalidSignatureRequest(
                    f"Previous input(s) set a max cosigners of {expected_quorum_n}, but this transaction is {output_quorum_n}"
                )

            # Be sure all xpubs are properly acocunted for
            if output_quorum_n != len(psbt_out.named_pubs):
                # TODO: doesn't handle case where the same xfp is >1 signers (surprisngly complex)
                raise InvalidSignatureRequest(
                    f"{len(hdpubkey_map)} xpubs supplied != {len(psbt_out.named_pubs)} named_pubs in PSBT change output."
                    "You may be able to get this wallet to cosign a sweep transaction (1-output) instead."
                )

            bip32_derivs = []
            for named_pub in psbt_out.named_pubs.values():
                # Match to corresponding xpub to validate that this xpub is a participant in this change output
                xfp = named_pub.root_fingerprint.hex()

                try:
                    hdpub = hdpubkey_map[xfp]
                except KeyError:
                    raise InvalidSignatureRequest(
                        f"Root fingerprint {xfp} for output #{index} not in the hdpubkey_map you supplied"
                        "Do a sweep transaction (1-output) if you want this wallet to cosign."
                    )

                trimmed_path = ltrim_path(named_pub.root_path, depth=hdpub.depth)
                if hdpub.traverse(trimmed_path).sec() != named_pub.sec():
                    raise InvalidSignatureRequest(
                        f"xpub {hdpub} with path {named_pub.root_path} does not appear to be part of output # {index}"
                        "You may be able to get this wallet to cosign a sweep transaction (1-output) instead."
                    )

                # this is very similar to what bitcoin-core's decodepsbt returns
                bip32_derivs.append(
                    {
                        "pubkey": named_pub.sec().hex(),
                        "master_fingerprint": xfp,
                        "path": named_pub.root_path,
                        "xpub": hdpub.xpub(),
                    }
                )

            # BIP67 sort order
            bip32_derivs = sorted(bip32_derivs, key=lambda k: k["pubkey"])

            # Confirm there aren't >1 change ouputs
            # (this is technically allowed but too sketchy to support)
            if change_sats or change_addr:
                raise InvalidSignatureRequest(
                    f"Cannot have >1 change output.\n{outputs_desc}"
                )
            change_addr = output_desc["addr"]
            change_sats = output_desc["sats"]

            output_desc["witness_script"] = str(psbt_out.witness_script)

        else:
            output_desc["is_change"] = False
            spends_count += 1
            spend_sats += output_desc["sats"]

            if spends_count > 1:
                # There is no concept of a single spend addr/amount for batch spends
                # Caller must interpret the batch spend from the returned outputs_desc
                spend_addr = ""
            else:
                spend_addr = output_desc["addr"]

        outputs_desc.append(output_desc)

    return {
        "total_sats": total_sats,
        "outputs_desc": outputs_desc,
        "change_addr": change_addr,
        "change_sats": change_sats,
        "spend_addr": spend_addr,
        "spend_sats": spend_sats,
        "is_batch_tx": spends_count > 1,
    }


def describe_basic_p2sh_multisig_tx(
    psbt: PSBT, xfp_for_signing=None, hdpubkey_map=None
):
    """
    Describe a typical p2sh multisig transaction in a human-readable way for
    manual verification before signing.

    This tool supports transactions with the following constraints:
    * ALL inputs have the exact same multisig wallet (quorum + xpubs)
    * All outputs are either spend or proven to be change.
    For UX reasons, there can not be >1 change address.

    An InvalidSignatureRequest Exception does not strictly mean there is a problem with the transaction, it is likely just too complex for simple summary.

    Due to the nature of how PSBT works, if your PSBT is slimmed down (doesn't contain xpubs AND prev TX hexes), you must supply a `hdpubkey_map` for ALL n xpubs:
      {
        'xfphex1': HDPublicKey1,
        'xfphex2': HDPublicKey2,
      }
    These HDPublicKey's will be traversed according to the paths given in the PSBT.

    TODOS:
      - add helper method that accepts an output descriptor, converts it into an hdpubkey_map, and then calls this method
      - add support for p2sh and other script types
    """

    psbt.validate()

    tx_fee_sats = psbt.tx_obj.fee()

    if not psbt.hd_pubs:
        raise InvalidSignatureRequest(
            "Cannot describe multisig PSBT without `hd_pubs` nor `hdpubkey_map`"
        )

    # build hdpubkey_map from PSBT's hdpubs
    hdpubkey_map = {}
    for hdpubkey in psbt.hd_pubs.values():
        hdpubkey_map[hdpubkey.root_fingerprint.hex()] = HDPublicKey.parse(
            hdpubkey.xpub()
        )

    inputs_described = describe_basic_inputs(psbt, hdpubkey_map=hdpubkey_map)
    total_input_sats = inputs_described["total_input_sats"]

    outputs_described = describe_basic_outputs(
        psbt,
        hdpubkey_map=hdpubkey_map,
        # Tool requires m-of-n be same for inputs as outputs
        expected_quorum_m=inputs_described["inputs_quorum_m"],
        expected_quorum_n=inputs_described["inputs_quorum_n"],
    )
    is_batch_tx = outputs_described["is_batch_tx"]
    total_output_sats = outputs_described["total_sats"]
    spend_sats = outputs_described["spend_sats"]
    spend_addr = outputs_described["spend_addr"]

    tx_fee_rounded = round(tx_fee_sats / total_input_sats * 100, 2)
    # comma separating satoshis for better display
    if is_batch_tx:
        spend_breakdown = "\n".join(
            [
                f"{x['addr']}: {x['sats']:,} sats"
                for x in outputs_described["outputs_desc"]
                if not x["is_change"]
            ]
        )
        tx_summary_text = f"Batch PSBT sends {spend_sats:,} sats with a fee of {tx_fee_sats:,} sats ({tx_fee_rounded}% of spend). Batch spend breakdown:\n{spend_breakdown}"
    else:
        tx_summary_text = f"PSBT sends {spend_sats:,} sats to {spend_addr} with a fee of {tx_fee_sats:,} sats ({tx_fee_rounded}% of spend)"

    return {
        # TX level:
        "txid": psbt.tx_obj.id(),
        "tx_summary_text": tx_summary_text,
        "locktime": psbt.tx_obj.locktime,
        "version": psbt.tx_obj.version,
        "network": psbt.network,
        "tx_fee_sats": tx_fee_sats,
        "total_input_sats": total_input_sats,
        "total_output_sats": total_output_sats,
        "spend_sats": spend_sats,
        "change_addr": outputs_described["change_addr"],
        "change_sats": outputs_described["change_sats"],
        "spend_addr": spend_addr,
        "is_batch_tx": is_batch_tx,
        # Input/output level
        "inputs_desc": inputs_described["inputs_desc"],
        "outputs_desc": outputs_described["outputs_desc"],
        "root_paths": inputs_described["root_paths_for_signing"],
    }


def describe_basic_psbt(psbt: PSBT, xfp_for_signing=None):
    psbt.validate()

    tx_fee_sats = psbt.tx_obj.fee()

    if not psbt.hd_pubs:
        raise InvalidSignatureRequest(
            "Cannot describe multisig PSBT without `hd_pubs` nor `hdpubkey_map`"
        )

    # build hdpubkey_map from PSBT's hdpubs
    hdpubkey_map = {}
    for hdpubkey in psbt.hd_pubs.values():
        hdpubkey_map[hdpubkey.root_fingerprint.hex()] = HDPublicKey.parse(
            hdpubkey.xpub()
        )

    # # These will be used for all inputs and change outputs
    # tx_quorum_m, tx_quorum_n = None, None

    inputs_described = describe_basic_inputs(psbt, hdpubkey_map=hdpubkey_map)
    total_input_sats = inputs_described["total_input_sats"]
    # total_input_sats = sum([x["sats"] for x in inputs_desc])

    outputs_described = describe_basic_outputs(
        psbt,
        hdpubkey_map=hdpubkey_map,
        # Tool requires m-of-n be same for inputs as outputs
        expected_quorum_m=inputs_described["inputs_quorum_m"],
        expected_quorum_n=inputs_described["inputs_quorum_n"],
    )
    is_batch_tx = outputs_described["is_batch_tx"]
    # total_output_sats = outputs_described["total_sats"]
    spend_sats = outputs_described["spend_sats"]
    spend_addr = outputs_described["spend_addr"]

    tx_fee_rounded = round(tx_fee_sats / total_input_sats * 100, 2)
    # comma separating satoshis for better display
    if is_batch_tx:
        spend_breakdown = "\n".join(
            [
                f"{x['addr']}: {x['sats']:,} sats"
                for x in outputs_described["outputs_desc"]
                if not x["is_change"]
            ]
        )
        tx_summary_text = f"Batch PSBT sends {spend_sats:,} sats with a fee of {tx_fee_sats:,} sats ({tx_fee_rounded}% of spend). Batch spend breakdown:\n{spend_breakdown}"
    else:
        tx_summary_text = f"PSBT sends {spend_sats:,} sats to {spend_addr} with a fee of {tx_fee_sats:,} sats ({tx_fee_rounded}% of spend)"

    to_return = {
        # TX level:
        "txid": psbt.tx_obj.id(),
        "tx_summary_text": tx_summary_text,
        "locktime": psbt.tx_obj.locktime,
        "version": psbt.tx_obj.version,
        "network": psbt.network,
        "tx_fee_sats": tx_fee_sats,
        "total_input_sats": total_input_sats,
        "output_spend_sats": spend_sats,
        "change_addr": outputs_described["change_addr"],
        "output_change_sats": outputs_described["change_sats"],
        "change_sats": total_input_sats - tx_fee_sats - spend_sats,
        "spend_addr": spend_addr,
        # Input/output level
        "inputs_desc": inputs_described,
        "outputs_desc": outputs_described,
    }

    if xfp_for_signing:
        if not inputs_described["root_paths_for_signing"]:
            # We confirmed above that all inputs have identical encumberance so we choose the first one as representative
            err = [
                "Did you enter a root fingerprint for another seed?",
                f"The xfp supplied ({xfp_for_signing}) does not correspond to the transaction inputs, which are {inputs_described['inputs_quorum_m']} of the following:",
                ", ".join(sorted(list(hdpubkey_map.keys()))),
            ]
            raise InvalidSignatureRequest("\n".join(err))

        to_return["root_paths"] = inputs_described["root_paths_for_signing"]

    return to_return
