# skrivesenteret-statistikk

Appen er opprinnelig utviklet av Carina Thanh-Tam Truong og vil fremover vedlikeholdes av [Kristin Botnen](https://www.ub.uio.no/om/ansatte/akademisk-skrivesenter/kristbot/). Den ble deploya på https://ub-www01.uio.no/skrivesenteret/ av [Dan Michael Heggø](https://www.ub.uio.no/om/ansatte/mednat/dsc/dmheggo/).

## Drift

Tjenesten kjører fra `/srv/skrivesenteret/` på serveren `ub-www01`. Tilgang  gis gjennom gruppemedlemskap i gruppen `ub-www01-skrivesenter`.

Systemd-tjenesten er konfigurert i `/etc/systemd/system/skrivesenteret.service`. For å omstarte den:

   sudo systemctl restart skrivesenteret

For å sjekke logger:

   sudo journalctl -u skrivesenteret

Ansvarlig for serveren er [UB-IT](https://www.uio.no/for-ansatte/drift/it-tjenester/ub/) / drift@ub.uio.no 
