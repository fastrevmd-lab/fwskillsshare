# Recommended Compliance Skills TODO

Recommended future compliance skills for this firewall / NGFW skill collection.

## Created

- [x] `cmmc-nist-800-171-ngfw-compliance` — CMMC Level 2 / NIST SP 800-171 CUI enclave scoping, boundary protection, remote access, external connections, audit logging, incident response, SSP evidence, and POA&M-style gap handling.

## Recommended next skills

1. [ ] `cis-controls-ngfw-compliance`
   - Broad reusable baseline for many organizations.
   - Map firewall evidence to CIS Controls v8 around network infrastructure management, secure configuration, access control, audit logs, malware defenses, data protection, vulnerability management, and incident response.

2. [ ] `iso27001-ngfw-compliance`
   - Enterprise and international compliance support.
   - Map firewall controls to ISO/IEC 27001:2022 Annex A areas including access control, network security, logging/monitoring, secure configuration, supplier access, change management, and incident management.
   - Keep language management-system oriented; do not imply a firewall alone satisfies ISO 27001.

3. [ ] `soc2-ngfw-compliance`
   - SaaS, MSP, and cloud-service-provider evidence support.
   - Map firewall/network controls to Trust Services Criteria such as CC6 logical access, CC7 system operations/monitoring, CC8 change management, and availability/security evidence.

4. [ ] `cjis-ngfw-compliance`
   - Law-enforcement and public-sector environments handling Criminal Justice Information.
   - Cover CJI segmentation, encryption, advanced authentication/MFA, remote access, logging, agency/vendor connectivity, wireless/mobile access, and CJIS Security Policy evidence.

5. [ ] `glba-ftc-safeguards-ngfw-compliance`
   - Financial institutions, lenders, insurance-adjacent organizations, and fintech.
   - Cover customer information systems, access controls, encryption, monitoring, vendor access, incident response, and risk-assessment linkage under GLBA / FTC Safeguards Rule expectations.

6. [ ] `nerc-cip-ngfw-compliance`
   - Electric utility / bulk electric system environments.
   - Cover Electronic Security Perimeters, BES Cyber Systems, Interactive Remote Access, access control, logging, change management, and mappings to CIP-005, CIP-007, CIP-010, and CIP-011.
   - Use strict NERC terminology and avoid generic IT-security shortcuts.

7. [ ] `iec62443-ngfw-compliance`
   - Industrial / OT firewall and segmentation work.
   - Cover zones and conduits, security levels, industrial DMZs, IT/OT segmentation, remote vendor access, legacy-system compensating controls, and firewall evidence.

8. [ ] `gdpr-ngfw-compliance`
   - Privacy/security-of-processing support.
   - Focus on how firewalls support GDPR Article 32 security of processing, data minimization by access restriction, breach detection/evidence, processor access, and third-party connectivity.
   - Avoid overclaiming “GDPR compliant firewall.”

9. [ ] `fedramp-ngfw-compliance`
   - Federal/cloud security work.
   - Map NGFW/firewall controls to NIST SP 800-53 Rev. 5 families such as AC, AU, CM, CP, IR, SC, SI, and RA.
   - Larger lift, but highly reusable for cloud and public-sector environments.

## Lower priority / conditional

- [ ] `sox-ngfw-compliance`
  - Consider only if there is a specific financial-reporting-system network-control use case.
  - SOX can involve firewall evidence around financially relevant systems, but it is less network-control-specific than PCI, HIPAA, CMMC, CJIS, NERC CIP, or IEC 62443.

## Suggested creation order

1. `cis-controls-ngfw-compliance`
2. `iso27001-ngfw-compliance`
3. `soc2-ngfw-compliance`
4. `cjis-ngfw-compliance`
5. `nerc-cip-ngfw-compliance` or `iec62443-ngfw-compliance`, depending on whether utility/energy or broader OT is the next priority
