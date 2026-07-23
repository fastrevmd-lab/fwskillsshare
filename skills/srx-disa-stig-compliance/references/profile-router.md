# SRX STIG Profile Router

## Minimum and conditional components

The DISA overview requires NDM and ALG for the SRX firewall management/RE and
firewall/PFE surfaces. Select IDPS and VPN only when the SRX performs those
functions. Establish role use from architecture, configuration, operational
state, and owner confirmation; an omitted input is not proof of nonuse.

| Scenario | Selected | Required gap |
|---|---|---|
| firewall only | NDM,ALG | none |
| firewall + IDPS | NDM,ALG,IDPS | none |
| firewall + VPN | NDM,ALG,VPN | none |
| firewall + IDPS + VPN | NDM,ALG,IDPS,VPN | none |
| role evidence unknown | NDM,ALG | IDPS/VPN scope unresolved |

## Selection procedure

1. Select NDM and ALG.
2. Look for IDP configuration, licenses, detector/database state, policy
   attachments, and architecture statements. If use is proved, select IDPS. If
   contradictory or incomplete, record an unresolved scope gap.
3. Look for IKE/IPsec configuration, active SAs, routing/tunnel interfaces,
   architecture statements, and owner confirmation. If network IPsec VPN use is
   proved, select VPN. If incomplete, record an unresolved scope gap.
4. Record unused-role evidence; omit that component rather than marking every
   rule Not Applicable.

## Other roles

An SRX may also act as a router, switch, remote-access gateway, or another
network/security component. These roles can require generic or product-specific
STIGs not bundled here. State the handoff and leave those results out of this
skill's totals. Do not imply that NDM/ALG/IDPS/VPN exhaust the enclave scope.
