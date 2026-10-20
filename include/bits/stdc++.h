// Wrapper around the real <bits/stdc++.h> so that a precompiled header can sit next to it.
//
// GCC looks for "bits/stdc++.h.gch" next to the first matching header on the include path.
// This file is that header; include_next skips it and pulls in the system copy.
// Build the .gch with: python3 scripts/pch.py
#pragma once
#include_next <bits/stdc++.h>
