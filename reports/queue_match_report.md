# Queue-to-Bottleneck Matching

Screening estimates: relief = capacity x capacity-factor x state-footprint weight, valued at the tie's measured congestion component, capped at the tie's annual gross flow. Not a production-cost simulation.

```
Queue-to-bottleneck matching (25 ties, 5 with measured spreads)
  PJM--NYIS (cap $29.5M/yr, gen side PJM, storage side NYIS):
    active: 761 projects, 85.5 GW, capped relief $29.5M/yr | withdrawn (lost): 4205 projects, 524.3 GW, $29.5M/yr
      AG2-582 [gas 2,100MW WV generation->PJM] relief $15.45M/yr
      AI2-431 [offshore_wind 2,139MW NJ generation->PJM] relief $12.87M/yr
      AI1-001 [offshore_wind 2,100MW NJ generation->PJM] relief $12.64M/yr
  MISO--SWPP (cap $18.9M/yr, gen side SWPP, storage side MISO):
    active: 705 projects, 156.5 GW, capped relief $18.9M/yr | withdrawn (lost): 1736 projects, 344.7 GW, $18.9M/yr
      GEN-2024-129 [gas 910MW KS generation->SWPP] relief $18.91M/yr
      GEN-2024-132 [gas 1,300MW OK generation->SWPP] relief $18.91M/yr
      GEN-2024-340 [gas 1,400MW OK generation->SWPP] relief $18.91M/yr
  CISO--SRP (cap $14.0M/yr, gen side CISO, storage side SRP):
    active: 250 projects, 68.0 GW, capped relief $14.0M/yr | withdrawn (lost): 1600 projects, 389.8 GW, $14.0M/yr
      1889 [wind_battery 1,525MW CA generation->CISO] relief $5.46M/yr
      1750 [offshore_wind 1,029MW CA generation->CISO] relief $4.74M/yr
      1745 [gas 656MW CA generation->CISO] relief $3.69M/yr
  MISO--SOCO (cap $7.2M/yr, gen side MISO, storage side SOCO):
    active: 1181 projects, 261.9 GW, capped relief $7.2M/yr | withdrawn (lost): 2360 projects, 467.9 GW, $7.2M/yr
      E0012 [gas 1,211MW WI generation->MISO] relief $7.23M/yr
      E0014 [gas 1,640MW LA generation->MISO] relief $7.23M/yr
      E0016 [gas 1,211MW WI generation->MISO] relief $7.23M/yr
  BPAT--CISO (cap $6.1M/yr, gen side CISO, storage side BPAT):
    active: 305 projects, 85.6 GW, capped relief $6.1M/yr | withdrawn (lost): 1616 projects, 393.6 GW, $6.1M/yr
      1889 [wind_battery 1,525MW CA generation->CISO] relief $4.36M/yr
      1750 [offshore_wind 1,029MW CA generation->CISO] relief $3.78M/yr
      1745 [gas 656MW CA generation->CISO] relief $2.95M/yr
```
