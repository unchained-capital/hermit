Hermit API Documentation
========================

This document is intended for developers working on Hermit, extending
Hermit, or integrating Hermit into some other program.  For end-user
documentation, see Hermit's `README
<https://github.com/unchained-capital/hermit>`_.

Hermit's codebase is split into three sections:

* a collection of functions which together constitute an API for
  configuration, input, & output

* classes to model cameras, displays, a bitcoin wallet, and signing
  bitcoin transactions

* a UI in the form of a command-line REPL

The functional API is documented below, while the classes are
documented on their own pages.

.. toctree::
   :maxdepth: 2

   hermit.config
   hermit.io
   hermit.qr
   hermit.keystore
   hermit.coordinator

API
---

The following methods are available in the top-level ``hermit``
namespace.

Configuration
~~~~~~~~~~~~~

.. automodule:: hermit.config
    :members: get_config

Input & Output
~~~~~~~~~~~~~~

.. automodule:: hermit.io
    :members: get_io, display_data_as_animated_qrs, read_data_from_animated_qrs

QR Codes
~~~~~~~~

.. automodule:: hermit.qr
    :members: create_qr, create_qr_sequence, qr_to_image, detect_qrs_in_image

Randomness
~~~~~~~~~~

.. automodule:: hermit.rng
    :members: max_entropy_estimate, max_self_entropy, max_kolmogorov_entropy_estimate
