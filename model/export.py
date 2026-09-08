"""Export every number behind the deck as CSV + one combined JSON."""
import os, sys, csv, json
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import model as M
D=os.path.join(HERE,"..","data"); os.makedirs(D,exist_ok=True)
def w(name, header, rows):
    with open(os.path.join(D,name),"w",newline="") as f:
        c=csv.writer(f); c.writerow(header); c.writerows(rows)
    return {"file":name,"header":header,"rows":rows}
J={}

# 1 ─ assumptions and their provenance
J['assumptions']=w("01_assumptions.csv",
 ["parameter","value","unit","status","source_or_test"],[
 ["Unit hardware (Ryzen AI Max+ 395, 128GB)",M.UNIT_HARDWARE,"AUD","VERIFIED","Retail listings; US$1,499-1,999 at AUD/USD 0.722"],
 ["Unit installation",M.UNIT_INSTALL,"AUD","ESTIMATE","TEST: firm installer quotes at volume"],
 ["Unit allocated platform + deployment",M.UNIT_PLATFORM,"AUD","ESTIMATE","Platform build amortised across fleet"],
 ["Unit all-in capex",M.UNIT_CAPEX,"AUD","DERIVED","hardware + install + platform"],
 ["Spark hardware (NVIDIA DGX Spark, 128GB)",M.SPARK_HARDWARE,"AUD","VERIFIED","US$4,699 (raised from $3,999 Feb 2026)"],
 ["Spark all-in capex",M.SPARK_CAPEX,"AUD","DERIVED","hardware + install + platform"],
 ["Unit node maintenance",M.UNIT_OM,"AUD/yr","ESTIMATE","TEST: support hours from first cohort"],
 ["Spark node maintenance",M.SPARK_OM,"AUD/yr","ESTIMATE","TEST: support hours from first cohort"],
 ["Unit average draw",M.UNIT_WATTS,"W","ESTIMATE","TEST: metered draw in pilot"],
 ["Spark average draw",M.SPARK_WATTS,"W","VERIFIED","240W supply rating (NVIDIA docs); 200W assumed average"],
 ["Grid purchase price",M.GRID_PRICE,"AUD/kWh","VERIFIED","Retail tariffs 2026 (30-40c)"],
 ["Surplus solar opportunity cost",M.SOLAR_OPP_COST,"AUD/kWh","VERIFIED","State regulators 2026; export 3-6c, many 0c midday"],
 ["Solar export tariff",M.EXPORT_TARIFF,"AUD/kWh","VERIFIED","State regulators 2026"],
 ["Share of node energy from surplus solar",M.SOLAR_SHARE,"ratio","ESTIMATE","TEST: metered solar vs grid split in pilot"],
 ["Company operating cost at 1,000 nodes",M.COMPANY_OPEX,"AUD/yr","ESTIMATE","~9 FTE + infrastructure + G&A"],
 ["Our share of a customer-owned node's pool",M.SOLD_POOL_SHARE,"ratio","ASSUMPTION","Commercial term, not yet contracted"],
 ["Customer price for a unit, installed",M.SOLD_PRICE,"AUD","ASSUMPTION","Commercial term, not yet tested"],
 ["AUD per USD",round(M.AUD_PER_USD,4),"ratio","VERIFIED","AUD/USD 0.722 at 7 Sep 2026"],
])

# 2 ─ per-node unit economics, three scenarios
rows=[]
for n,lbl in ((M.U_FLOOR,"floor"),(M.U_BASE,"base"),(M.U_UP,"upside"),(M.S_BASE,"spark (base case)")):
    rows.append([lbl,n.sc.tok_s,n.sc.hours,f"{n.sc.utilisation:.0%}",n.sc.price,
                 round(n.tokens/1e6),round(n.gross),f"{n.sc.owner_share:.0%}",round(n.to_owner),
                 round(n.energy),round(n.om),round(n.net),n.capex,round(n.payback,2),f"{n.roc:.0%}"])
J['unit_economics']=w("02_unit_economics.csv",
 ["scenario","throughput_tok_s","hours_per_day","paid_utilisation","price_aud_per_M_tokens",
  "tokens_sold_M_per_yr","gross_revenue_aud","homeowner_share","homeowner_paid_aud",
  "energy_aud","maintenance_aud","net_cash_aud","capex_aud","payback_years","return_on_capital"],rows)

# 3 ─ cost stack (base unit)
u=M.U_BASE; tot=u.to_owner+M.UNIT_OM+u.energy
J['cost_stack']=w("03_cost_stack.csv",["line_item","annual_aud","note"],[
 ["Homeowner revenue share",round(u.to_owner),"25% of gross"],
 ["Node maintenance",round(M.UNIT_OM),"support, spares, replacement"],
 ["Electricity",round(u.energy),f"{u.kwh:.0f} kWh/yr, {M.SOLAR_SHARE:.0%} surplus solar"],
 ["Land",0,"the home already exists"],["Building & cooling",0,"the home already exists"],
 ["Grid connection",0,"already connected"],["Physical security & staff",0,"the household"],
 ["TOTAL operating cost",round(tot),""],
 ["Gross revenue",round(u.gross),""],
 ["Gross margin",f"{(u.gross-tot)/u.gross:.1%}",""],
])

# 4 ─ sensitivity
def pb(**kw):
    sc=M.Scenario(**{**M.BASE.__dict__,**kw}); return M.UNIT_CAPEX/M.Node(sc,M.UNIT_CAPEX,M.UNIT_OM,M.UNIT_WATTS).net
J['sensitivity']=w("04_sensitivity.csv",["variable","low_value","high_value","payback_at_worst_yr","payback_at_best_yr","swing_yr"],[
 ["Throughput (tok/s)",M.FLOOR.tok_s,M.UPSIDE.tok_s,round(pb(tok_s=M.FLOOR.tok_s),2),round(pb(tok_s=M.UPSIDE.tok_s),2),round(pb(tok_s=M.FLOOR.tok_s)-pb(tok_s=M.UPSIDE.tok_s),2)],
 ["Sell price (AUD/M tokens)",M.FLOOR.price,M.UPSIDE.price,round(pb(price=M.FLOOR.price),2),round(pb(price=M.UPSIDE.price),2),round(pb(price=M.FLOOR.price)-pb(price=M.UPSIDE.price),2)],
 ["Paid utilisation",M.FLOOR.utilisation,M.UPSIDE.utilisation,round(pb(utilisation=M.FLOOR.utilisation),2),round(pb(utilisation=M.UPSIDE.utilisation),2),round(pb(utilisation=M.FLOOR.utilisation)-pb(utilisation=M.UPSIDE.utilisation),2)],
 ["Hardware cost (AUD)",3600,2000,round(4800/M.U_BASE.net,2),round(3200/M.U_BASE.net,2),round(4800/M.U_BASE.net-3200/M.U_BASE.net,2)],
 ["Homeowner share",M.FLOOR.owner_share,M.UPSIDE.owner_share,round(pb(owner_share=M.FLOOR.owner_share),2),round(pb(owner_share=M.UPSIDE.owner_share),2),round(pb(owner_share=M.FLOOR.owner_share)-pb(owner_share=M.UPSIDE.owner_share),2)],
])

# 5 ─ fleet
F=M.FLEET; mixes=[]
for frac,lbl in ((1.0,"all company-owned"),(0.5,"50/50"),(0.0,"all customer-owned")):
    c,k,o=F.mix(frac)
    mixes.append([lbl,round(F.gross),round(c),round(F.opex),round(o),round(k),
                  (f"{o/k:.0%}" if k else "n/a"),(round(k/o,1) if o>0 and k else "never")])
J['fleet']=w("05_fleet_1000_nodes.csv",
 ["ownership_mix","gross_revenue_aud","node_contribution_aud","company_opex_aud",
  "operating_cash_aud","capital_deployed_aud","return_on_capital","fleet_payback_years"],mixes)
J['fleet_breakeven']=w("06_fleet_breakeven.csv",["metric","value"],[
 ["Fleet composition",f"{F.units} units + {F.sparks} Spark-class"],
 ["Average contribution per owned node",round(F.avg_owned)],
 ["Average contribution per sold node",round(F.avg_sold)],
 ["Break-even fleet, company-owned",round(F.breakeven_owned)],
 ["Break-even fleet, customer-owned",round(F.breakeven_sold)],
 ["Capital advantage",f"{F.breakeven_sold/F.breakeven_owned:.1f}x"],
])

# 6 ─ arbitrage
J['arbitrage']=w("07_arbitrage.csv",["use_of_one_kWh","value_aud_per_kWh","source"],[
 ["Exported to the grid",M.EXPORT_TARIFF,"State regulators 2026; many retailers 0c midday"],
 ["Bought back at night",M.GRID_PRICE,"Retail tariffs 2026"],
 ["Converted to AI tokens",round(M.KWH_AS_TOKENS,2),"Base case: gross revenue / annual kWh"],
 ["Ratio vs export",f"{M.KWH_RATIO:.0f}x",""],
])

# 7 ─ market and supply
J['market']=w("08_market_and_supply.csv",["metric","value","unit","source"],[
 ["TAM: Australian AI market by 2030",M.TAM_2030,"AUD","Grand View Research / consensus (US$9.8B)"],
 ["SAM: AI-optimised infrastructure spend 2026",M.SAM_2026,"AUD","IDC Australia 2026"],
 ["SAM 2025",round(M.SAM_2025),"AUD","Derived from +128.4% YoY"],
 ["SAM growth YoY",f"{(M.SAM_GROWTH-1):.1%}","","IDC Australia 2026"],
 ["SOM at 1,000 nodes",round(M.SOM_1K),"AUD","Base case x 1,000"],
 ["SOM at 10,000 nodes",round(M.SOM_10K),"AUD","Base case x 10,000"],
 ["Share of SAM at 1,000 nodes",f"{M.SHARE_1K:.2%}","",""],
 ["Share of SAM at 10,000 nodes",f"{M.SHARE_10K:.2%}","",""],
 ["Homes with rooftop solar",M.SOLAR_HOMES,"homes","DCCEEW / Clean Energy Regulator"],
 ["...owner-occupied",round(M.SOLAR_HOMES*M.OWNER_OCCUPIED),"homes","ESTIMATE 80%"],
 ["...in serviceable areas",round(M.SOLAR_HOMES*M.OWNER_OCCUPIED*M.SERVICEABLE),"homes","ESTIMATE 70%"],
 ["...physically suitable (eligible)",round(M.ELIGIBLE_HOMES),"homes","ESTIMATE 75%"],
 ["Eligible share needed for 10,000 nodes",f"{M.ELIGIBLE_SHARE_10K:.2%}","",""],
 ["National rooftop solar output",M.ROOFTOP_TWH,"TWh/yr","~28.3 GW fleet"],
 ["Energy drawn by 10,000 nodes",f"{M.ENERGY_SHARE_10K:.3%}","of national output",""],
])

# 8 ─ demand segments
J['demand']=w("09_demand_segments.csv",["segment","size","unit","note","source"],[
 ["Universities & research",16.4e9,"AUD/yr","Higher-education R&D, +17% in two years. Beachhead: no classification barrier","ABS 2024 release"],
 ["Government",6.0e9,"AUD/yr","Commonwealth ICT procurement. GATED: sensitive/PROTECTED needs PSPF-zoned facilities a home cannot meet","DTA Hosting Certification Framework; Cloud Policy 1 Jul 2026"],
 ["Business using AI",337773,"businesses","12% of 2,814,778 actively trading","ABS, 30 June 2026"],
 ["All Australian businesses",2814778,"businesses","","ABS, 30 June 2026"],
 ["AI-optimised infrastructure spend",946e6,"AUD/yr","+128% YoY","IDC Australia 2026"],
])

# 9 ─ external benchmarks used
J['benchmarks']=w("10_benchmarks.csv",["benchmark","value","unit","source"],[
 ["Qwen3.8 Flash output price",0.58,"AUD/M tokens","Published rates, converted at 0.722"],
 ["Llama 3.3 70B price (low)",0.82,"AUD/M tokens","Groq / Together / Fireworks"],
 ["Llama 3.3 70B price (high)",1.25,"AUD/M tokens","Groq / Together / Fireworks"],
 ["Global average token cost",1.61,"AUD/M tokens","Industry tracking, Aug 2026"],
 ["MiniMax M2 output price",1.64,"AUD/M tokens","CNY 8.4/M published"],
 ["SunStack blended price (modelled)",M.BASE.price,"AUD/M tokens","ESTIMATE"],
 ["Frontier output price (low)",21,"AUD/M tokens","GPT/Claude class"],
 ["Frontier output price (high)",104,"AUD/M tokens","GPT/Claude class"],
 ["DGX Spark gpt-oss 120B single-stream",33.53,"tok/s","Dendro Logic concurrency benchmark 2026"],
 ["DGX Spark gpt-oss 120B at 256 concurrent",862.84,"tok/s","Dendro Logic concurrency benchmark 2026"],
 ["DGX Spark Nemotron 49B single-stream",5.79,"tok/s","Dendro Logic concurrency benchmark 2026"],
 ["DGX Spark Nemotron 49B at 256 concurrent",695.11,"tok/s","Dendro Logic concurrency benchmark 2026"],
 ["SunStack modelled throughput",M.BASE.tok_s,"tok/s","ESTIMATE: ~1/3 of benchmarked peak"],
 ["Ryzen AI Max+ 395 memory bandwidth",256,"GB/s","AMD specifications"],
 ["DGX Spark memory bandwidth",273,"GB/s","NVIDIA specifications"],
 ["Ryzen bandwidth per A$1,000",round(256/(M.UNIT_HARDWARE/1000)),"GB/s",""],
 ["Spark bandwidth per A$1,000",round(273/(M.SPARK_HARDWARE/1000)),"GB/s",""],
 ["Data centre average PUE",1.52,"ratio","Uptime Institute Global Data Center Survey 2026"],
 ["Origin VPP connected services",100000,"households","Origin Energy / IEEFA 2026"],
 ["Home batteries installed",500000,"batteries","PM's Office, 14 Aug 2026"],
])

# 10 ─ capital
J['capital']=w("11_capital.csv",["metric","value","unit"],[
 ["Capital already committed",2.4e6,"AUD (grants + equity)"],
 ["Units per A$1M deployed",round(M.PER_M_UNITS),"units"],
 ["Gross revenue added per A$1M",round(M.PER_M_GROSS),"AUD/yr"],
 ["Net cash added per A$1M",round(M.PER_M_NET),"AUD/yr"],
 ["Payback on A$1M",round(1e6/M.PER_M_NET,2),"years"],
 ["Use of funds: fleet & hardware",0.55,"share"],
 ["Use of funds: engineering",0.25,"share"],
 ["Use of funds: field ops & install",0.12,"share"],
 ["Use of funds: go-to-market",0.08,"share"],
])

json.dump(J, open(os.path.join(D,"sunstack-deck-data.json"),"w"), indent=1, default=str)
print("wrote", len(J)+1, "files to data/")
for k,v in J.items(): print(f"   {v['file']:32} {len(v['rows']):>3} rows")
