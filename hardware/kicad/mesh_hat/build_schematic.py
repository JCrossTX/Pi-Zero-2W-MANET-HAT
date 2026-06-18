#!/usr/bin/env python3
"""Generate the completed ZERO 2W MESH HAT schematic.

Loads the user's existing schematic (J1 header + ID-EEPROM block, untouched) and
ADDS the radios, power tree, USB front-end, RF front-ends, status LEDs and their
passives.  Connectivity is by net-label placed exactly on each pin endpoint
(geometry verified against the user's own wiring).  Labels that reuse the header's
exact net strings (e.g. 'GPIO10{slash}SPI0.MOSI') auto-connect to J1.

Symbols come from the user's stock KiCad-10 libraries (symbols.zip) + the custom
ZERO2W_MeshHat lib.  No symbol inheritance is used (all self-contained).
"""
import sys, os, copy, uuid, math
from kiutils.schematic import Schematic
from kiutils.symbol import SymbolLib
from kiutils.items.schitems import LocalLabel, NoConnect
from kiutils.items.common import Position

STOCK = "/tmp/symcheck/symbols"                       # extracted symbols.zip
CUSTOM = "/home/user/Pi-Zero-2W-MANET-HAT/hardware/kicad/mesh_hat/ZERO2W_MeshHat.kicad_sym"
SRC = sys.argv[1]
OUT = sys.argv[2]

NC = None  # no-connect sentinel

# ---- net name constants (match the user's existing power nets) ----
G="GND"; V5="+5V"; V33="+3V3"
RAD="+3V3_RAD"; GNS="+3V3_GNSS"; VBUS="VBUS_USB"; V5SW="+5V_SW"
DP="USB_DP"; DM="USB_DM"; RF9="RF_900"; RFG="RF_GNSS"

# header nets (exact strings as stored in the user's sheet)
def H(s): return s
MOSI="GPIO10{slash}SPI0.MOSI"; MISO="GPIO9{slash}SPI0.MISO"; SCLK="GPIO11{slash}SPI0.SCLK"
CE0="GPIO8{slash}SPI0.CE0"; SDA="GPIO2{slash}SDA1"; SCL="GPIO3{slash}SCL1"
TXD="GPIO14{slash}TXD0"; RXD="GPIO15{slash}RXD0"; PPS="GPIO18{slash}PCM.CLK"
PWM0="GPIO12{slash}PWM0"; PWM1="GPIO13{slash}PWM1"

# ---- components: (lib, entry, ref, value, footprint, {pin#: net}) ----
COMPONENTS = [
 # ---------- MM8108 LoRa-mesh radio ----------
 ("ZERO2W_MeshHat","MM8108-MF15457","U2","MM8108-MF15457","cm4mesh:Morse_MM8108-MF15457_LGA38_11x10",
   {"1":G,"2":RF9,"3":G,"4":"GPIO17","5":"GPIO24","6":NC,"7":NC,"8":NC,"9":NC,"10":RAD,
    "11":G,"12":MISO,"13":CE0,"14":"GPIO5","15":"MM_D2","16":MOSI,"17":SCLK,"18":NC,"19":NC,
    "20":G,"21":NC,"22":RAD,"23":G,"24":RAD,"25":NC,"26":G,"27":NC,"28":NC,"29":"GPIO25",
    "30":G,"31":NC,"32":NC,"33":NC,"34":NC,"35":NC,"36":NC,"37":NC,"38":G}),
 # ---------- NEO-M9N GNSS ----------
 ("ZERO2W_MeshHat","NEO-M9N-00B","U3","NEO-M9N-00B","cm4mesh:ublox_NEO-M9N_LCC24_12x16",
   {"1":"NEO_SAFE","2":"NEO_DSEL","3":PPS,"4":"GPIO22","5":NC,"6":NC,"7":NC,"8":"GPIO27",
    "9":"NEO_VCCRF","10":G,"11":"NEO_RFIN","12":G,"13":G,"14":NC,"15":NC,"16":NC,"17":NC,
    "18":SDA,"19":SCL,"20":RXD,"21":TXD,"22":GNS,"23":GNS,"24":G}),
 # ---------- buck 5V->3V3 (AP63200WU, SOT-23-6) ----------
 ("Regulator_Switching","AP63200WU","U4","AP63200WU","Package_TO_SOT_SMD:SOT-23-6",
   {"1":"BUCK_FB","2":V5SW,"3":V5SW,"4":G,"5":"BUCK_SW","6":"BUCK_BST"}),
 # ---------- input/inrush load switch (MIC2007, SOT-23-6) ----------
 ("Power_Management","MIC2007YM6","U5","MIC2007YM6","Package_TO_SOT_SMD:SOT-23-6",
   {"1":V5,"2":G,"3":V5,"4":"U5_ILIM","5":NC,"6":V5SW}),
 # ---------- radio-rail load switch (MIC2007, EN=GPIO23) ----------
 ("Power_Management","MIC2007YM6","U6","MIC2007YM6","Package_TO_SOT_SMD:SOT-23-6",
   {"1":V33,"2":G,"3":"GPIO23","4":"U6_ILIM","5":NC,"6":RAD}),
 # ---------- USB-C VBUS switch (RT9742, SOT-23-5) ----------
 ("Power_Management","RT9742AGJ5F","U7","RT9742AGJ5F","Package_TO_SOT_SMD:SOT-23-5",
   {"1":VBUS,"2":G,"3":NC,"4":V5,"5":V5}),
 # ---------- supervisor / reset (TPS3839, SOT-23-5) ----------
 ("Power_Supervisor","TPS3839DBZ","U8","TPS3839DBL30","Package_TO_SOT_SMD:SOT-23-5",
   {"1":G,"2":"GPIO17","3":V33}),
 # ---------- USB ESD (USBLC6-2, SOT-23-6) ----------
 ("Power_Protection","USBLC6-2P6","U9","USBLC6-2P6","Package_TO_SOT_SMD:SOT-23-6",
   {"1":DP,"2":G,"3":DM,"4":DM,"5":V5,"6":DP}),
 # ---------- connectors ----------
 ("Connector","Conn_Coaxial","J2","U.FL_900M","cm4mesh:U.FL_Hirose_U.FL-R-SMT-1_Vertical",
   {"1":RF9,"2":G}),
 ("Connector","Conn_Coaxial","J3","U.FL_GNSS","cm4mesh:U.FL_Hirose_U.FL-R-SMT-1_Vertical",
   {"1":RFG,"2":G}),
 ("Connector","USB_C_Receptacle_USB2.0_16P","J6","USB_C","cm4mesh:USB_C_Receptacle_GCT_USB4085",
   {"A1":G,"A4":VBUS,"A5":"USBC_CC1","A6":DP,"A7":DM,"A8":NC,"A9":VBUS,"A12":G,
    "B1":G,"B4":VBUS,"B5":"USBC_CC2","B6":DP,"B7":DM,"B8":NC,"B9":VBUS,"B12":G,"SH":G}),
 ("Connector","USB_B_Micro","J7","USB_MicroB","Connector_USB:USB_Micro-B_Molex_47346-0001",
   {"1":V5,"2":DM,"3":DP,"4":NC,"5":G,"SH":G}),
 # ---------- diodes / TVS / ESD ----------
 ("Device","D_TVS","D1","SMAJ5.0A","Diode_SMD:D_SMA",{"1":V5,"2":G}),
 ("Diode","ESD9B5.0ST5G","D2","ESD9B5.0ST5G","Diode_SMD:D_SOD-323",{"1":RF9,"2":G}),
 ("Diode","ESD9B5.0ST5G","D3","ESD9B5.0ST5G","Diode_SMD:D_SOD-323",{"1":RFG,"2":G}),
 # ---------- status LEDs (pin1=K, pin2=A) ----------
 ("Device","LED","D4","PWR","LED_SMD:LED_0603_1608Metric",{"1":G,"2":"LED_PWR_A"}),
 ("Device","LED","D5","FIX","LED_SMD:LED_0603_1608Metric",{"1":G,"2":"LED_FIX_A"}),
 ("Device","LED","D6","TX","LED_SMD:LED_0603_1608Metric",{"1":G,"2":"LED_TX_A"}),
 # ---------- magnetics ----------
 ("Device","L","L1","2.2uH","cm4mesh:L_Wuerth_MAPI-4020",{"1":"BUCK_SW","2":V33}),
 ("Device","L","L2","27nH","Inductor_SMD:L_0402_1005Metric",{"1":"NEO_VCCRF","2":RFG}),
 ("Device","FerriteBead","FB1","600R@100M","Inductor_SMD:L_0603_1608Metric",{"1":V33,"2":GNS}),
 # ---------- buck passives ----------
 ("Device","R_Small","R3","31.6k","Resistor_SMD:R_0402_1005Metric",{"1":V33,"2":"BUCK_FB"}),
 ("Device","R_Small","R4","10k","Resistor_SMD:R_0402_1005Metric",{"1":"BUCK_FB","2":G}),
 ("Device","C_Small","C2","100n","Capacitor_SMD:C_0402_1005Metric",{"1":"BUCK_BST","2":"BUCK_SW"}),
 ("Device","C_Small","C3","10uF","Capacitor_SMD:C_0805_2012Metric",{"1":V5SW,"2":G}),
 ("Device","C_Small","C4","22uF","Capacitor_SMD:C_0805_2012Metric",{"1":V33,"2":G}),
 ("Device","R_Small","R5","20k","Resistor_SMD:R_0402_1005Metric",{"1":"U5_ILIM","2":G}),
 ("Device","R_Small","R6","20k","Resistor_SMD:R_0402_1005Metric",{"1":"U6_ILIM","2":G}),
 # ---------- USB-C CC (sink) ----------
 ("Device","R_Small","R7","5.1k","Resistor_SMD:R_0402_1005Metric",{"1":"USBC_CC1","2":G}),
 ("Device","R_Small","R8","5.1k","Resistor_SMD:R_0402_1005Metric",{"1":"USBC_CC2","2":G}),
 # ---------- MM8108 rail decoupling + pulls ----------
 ("Device","C_Small","C5","10uF","Capacitor_SMD:C_0805_2012Metric",{"1":RAD,"2":G}),
 ("Device","C_Small","C6","100n","Capacitor_SMD:C_0402_1005Metric",{"1":RAD,"2":G}),
 ("Device","C_Small","C7","100n","Capacitor_SMD:C_0402_1005Metric",{"1":RAD,"2":G}),
 ("Device","C_Small","C8","100n","Capacitor_SMD:C_0402_1005Metric",{"1":RAD,"2":G}),
 ("Device","R_Small","R9","10k","Resistor_SMD:R_0402_1005Metric",{"1":"GPIO17","2":RAD}),
 ("Device","R_Small","R10","10k","Resistor_SMD:R_0402_1005Metric",{"1":"MM_D2","2":RAD}),
 # ---------- NEO rail decoupling + pulls + RF ----------
 ("Device","C_Small","C9","10uF","Capacitor_SMD:C_0805_2012Metric",{"1":GNS,"2":G}),
 ("Device","C_Small","C10","100n","Capacitor_SMD:C_0402_1005Metric",{"1":GNS,"2":G}),
 ("Device","C_Small","C11","10n","Capacitor_SMD:C_0402_1005Metric",{"1":"NEO_VCCRF","2":G}),
 ("Device","C_Small","C12","100p","Capacitor_SMD:C_0402_1005Metric",{"1":"NEO_RFIN","2":RFG}),
 ("Device","R_Small","R11","10k","Resistor_SMD:R_0402_1005Metric",{"1":"NEO_SAFE","2":GNS}),
 ("Device","R_Small","R12","10k","Resistor_SMD:R_0402_1005Metric",{"1":"NEO_DSEL","2":GNS}),
 ("Device","R_Small","R13","10k","Resistor_SMD:R_0402_1005Metric",{"1":"GPIO27","2":GNS}),
 # ---------- LED series resistors ----------
 ("Device","R_Small","R14","1k","Resistor_SMD:R_0402_1005Metric",{"1":V33,"2":"LED_PWR_A"}),
 ("Device","R_Small","R15","1k","Resistor_SMD:R_0402_1005Metric",{"1":PWM0,"2":"LED_FIX_A"}),
 ("Device","R_Small","R16","1k","Resistor_SMD:R_0402_1005Metric",{"1":PWM1,"2":"LED_TX_A"}),
]

# ---------------------------------------------------------------------------
def rot(x, y, a):
    a = math.radians(a); c, s = round(math.cos(a)), round(math.sin(a))
    return x*c - y*s, x*s + y*c

def load_lib_symbol(lib, entry):
    path = os.path.join(STOCK, lib + ".kicad_sym")
    if lib == "ZERO2W_MeshHat":
        path = CUSTOM
    L = SymbolLib().from_file(path)
    for s in L.symbols:
        if s.entryName == entry:
            return s
    raise KeyError(f"{lib}:{entry}")

def pin_positions(libsym):
    """return list of (number, x, y) connection points in symbol coords."""
    out = []
    for u in libsym.units:
        for p in u.pins:
            out.append((p.number, p.position.X, p.position.Y))
    return out

def main():
    sch = Schematic().from_file(SRC)
    try:
        sch.paper.paperSize = "A2"      # enlarge sheet to contain added parts
    except Exception:
        pass
    proj_name = sch.schematicSymbols[0].instances[0].name
    sheet_path = sch.schematicSymbols[0].instances[0].paths[0].sheetInstancePath
    template = copy.deepcopy(next(s for s in sch.schematicSymbols
                                  if any(p.key=="Reference" and p.value=="R1" for p in s.properties)))
    label_fx = copy.deepcopy(sch.labels[0].effects)
    have_libs = {s.libId for s in sch.libSymbols}

    # grid placement (clear of existing content at x<=120)
    GX0, GY0, DX, DY, COLS = 150.0, 45.0, 60.0, 62.0, 8
    netpins = {}      # net -> list of (ref,pin,(x,y))
    coord_use = {}    # (x,y) -> net  (overlap guard)
    n_lbl = n_nc = 0

    for i, (lib, entry, ref, val, fp, nets) in enumerate(COMPONENTS):
        libid = f"{lib}:{entry}"
        libsym = load_lib_symbol(lib, entry)
        if libid not in have_libs:
            ls = copy.deepcopy(libsym); ls.libId = libid
            sch.libSymbols.append(ls); have_libs.add(libid)

        gx = GX0 + (i % COLS) * DX
        gy = GY0 + (i // COLS) * DY

        # placed symbol from template
        sym = copy.deepcopy(template)
        sym.libId = libid; sym.entryName = entry; sym.libraryNickname = lib
        sym.uuid = str(uuid.uuid4()); sym.unit = 1
        sym.position = Position(gx, gy, 0)
        props = {p.key: p for p in sym.properties}
        props["Reference"].value = ref;   props["Reference"].position = Position(gx, gy-2, 0)
        props["Value"].value = val;       props["Value"].position = Position(gx, gy+2, 0)
        if "Footprint" in props:
            props["Footprint"].value = fp; props["Footprint"].position = Position(gx, gy+4, 0)
        sym.instances[0].name = proj_name
        sym.instances[0].paths[0].sheetInstancePath = sheet_path
        sym.instances[0].paths[0].reference = ref
        sym.instances[0].paths[0].unit = 1
        sch.schematicSymbols.append(sym)

        # labels / no-connects on each pin
        for num, px, py in pin_positions(libsym):
            rx, ry = rot(px, py, 0)
            X = round(gx + rx, 4); Y = round(gy - ry, 4)
            net = nets.get(num, NC)
            if net is NC:
                sch.noConnects.append(NoConnect(position=Position(X, Y, 0),
                                                uuid=str(uuid.uuid4())))
                n_nc += 1
            else:
                if (X, Y) in coord_use and coord_use[(X, Y)] != net:
                    raise RuntimeError(f"OVERLAP at {(X,Y)}: {coord_use[(X,Y)]} vs {net} ({ref}.{num})")
                coord_use[(X, Y)] = net
                lab = LocalLabel(text=net, position=Position(X, Y, 0),
                                 effects=copy.deepcopy(label_fx), uuid=str(uuid.uuid4()))
                sch.labels.append(lab); n_lbl += 1
                netpins.setdefault(net, []).append((ref, num, (X, Y)))

    sch.to_file(OUT)
    # re-add the embedded_fonts flag kiutils drops
    t = open(OUT).read()
    if "embedded_fonts" not in t:
        t = t.rstrip()
        assert t.endswith(")")
        t = t[:-1] + "\t(embedded_fonts no)\n)\n"
        open(OUT, "w").write(t)

    # duplicate-refdes guard (incl. the user's existing parts)
    refs = [p.value for s in sch.schematicSymbols for p in s.properties
            if p.key == "Reference" and not p.value.startswith("#")]
    dups = sorted({r for r in refs if refs.count(r) > 1})
    if dups:
        raise RuntimeError(f"DUPLICATE refdes: {dups}")

    # net report
    if len(sys.argv) > 3:
        with open(sys.argv[3], "w") as f:
            f.write("# ZERO 2W MESH HAT - generated net report\n\n")
            f.write(f"{len(COMPONENTS)} added parts, {len(netpins)} new nets, "
                    f"{n_lbl} labels, {n_nc} no-connects.\n\n")
            for net in sorted(netpins):
                mem = ", ".join(f"{r}.{p}" for r, p, _ in netpins[net])
                f.write(f"- **{net}** : {mem}\n")

    print(f"added {len(COMPONENTS)} parts | labels {n_lbl} | no-connects {n_nc} | "
          f"nets {len(netpins)} | dup-refs {dups or 'none'}")
    return sch, netpins

if __name__ == "__main__":
    main()
