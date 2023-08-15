import typing
import timeit
import math
import random


def sine_value(angle):
    return math.sin(math.radians(angle))


def precomputed_sine(
    angle: typing.Literal[
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
        24,
        25,
        26,
        27,
        28,
        29,
        30,
        31,
        32,
        33,
        34,
        35,
        36,
        37,
        38,
        39,
        40,
        41,
        42,
        43,
        44,
        45,
        46,
        47,
        48,
        49,
        50,
        51,
        52,
        53,
        54,
        55,
        56,
        57,
        58,
        59,
        60,
        61,
        62,
        63,
        64,
        65,
        66,
        67,
        68,
        69,
        70,
        71,
        72,
        73,
        74,
        75,
        76,
        77,
        78,
        79,
        80,
        81,
        82,
        83,
        84,
        85,
        86,
        87,
        88,
        89,
        90,
        91,
        92,
        93,
        94,
        95,
        96,
        97,
        98,
        99,
        100,
        101,
        102,
        103,
        104,
        105,
        106,
        107,
        108,
        109,
        110,
        111,
        112,
        113,
        114,
        115,
        116,
        117,
        118,
        119,
        120,
        121,
        122,
        123,
        124,
        125,
        126,
        127,
        128,
        129,
        130,
        131,
        132,
        133,
        134,
        135,
        136,
        137,
        138,
        139,
        140,
        141,
        142,
        143,
        144,
        145,
        146,
        147,
        148,
        149,
        150,
        151,
        152,
        153,
        154,
        155,
        156,
        157,
        158,
        159,
        160,
        161,
        162,
        163,
        164,
        165,
        166,
        167,
        168,
        169,
        170,
        171,
        172,
        173,
        174,
        175,
        176,
        177,
        178,
        179,
        180,
        181,
        182,
        183,
        184,
        185,
        186,
        187,
        188,
        189,
        190,
        191,
        192,
        193,
        194,
        195,
        196,
        197,
        198,
        199,
        200,
        201,
        202,
        203,
        204,
        205,
        206,
        207,
        208,
        209,
        210,
        211,
        212,
        213,
        214,
        215,
        216,
        217,
        218,
        219,
        220,
        221,
        222,
        223,
        224,
        225,
        226,
        227,
        228,
        229,
        230,
        231,
        232,
        233,
        234,
        235,
        236,
        237,
        238,
        239,
        240,
        241,
        242,
        243,
        244,
        245,
        246,
        247,
        248,
        249,
        250,
        251,
        252,
        253,
        254,
        255,
        256,
        257,
        258,
        259,
        260,
        261,
        262,
        263,
        264,
        265,
        266,
        267,
        268,
        269,
        270,
        271,
        272,
        273,
        274,
        275,
        276,
        277,
        278,
        279,
        280,
        281,
        282,
        283,
        284,
        285,
        286,
        287,
        288,
        289,
        290,
        291,
        292,
        293,
        294,
        295,
        296,
        297,
        298,
        299,
        300,
        301,
        302,
        303,
        304,
        305,
        306,
        307,
        308,
        309,
        310,
        311,
        312,
        313,
        314,
        315,
        316,
        317,
        318,
        319,
        320,
        321,
        322,
        323,
        324,
        325,
        326,
        327,
        328,
        329,
        330,
        331,
        332,
        333,
        334,
        335,
        336,
        337,
        338,
        339,
        340,
        341,
        342,
        343,
        344,
        345,
        346,
        347,
        348,
        349,
        350,
        351,
        352,
        353,
        354,
        355,
        356,
        357,
        358,
        359,
        360,
    ]
):
    match angle:
        case 0:
            return 0.0
        case 1:
            return 0.01745240643728351
        case 2:
            return 0.03489949670250097
        case 3:
            return 0.052335956242943835
        case 4:
            return 0.0697564737441253
        case 5:
            return 0.08715574274765817
        case 6:
            return 0.10452846326765347
        case 7:
            return 0.12186934340514748
        case 8:
            return 0.13917310096006544
        case 9:
            return 0.15643446504023087
        case 10:
            return 0.17364817766693033
        case 11:
            return 0.1908089953765448
        case 12:
            return 0.20791169081775934
        case 13:
            return 0.224951054343865
        case 14:
            return 0.24192189559966773
        case 15:
            return 0.25881904510252074
        case 16:
            return 0.27563735581699916
        case 17:
            return 0.29237170472273677
        case 18:
            return 0.3090169943749474
        case 19:
            return 0.3255681544571567
        case 20:
            return 0.3420201433256687
        case 21:
            return 0.35836794954530027
        case 22:
            return 0.374606593415912
        case 23:
            return 0.39073112848927377
        case 24:
            return 0.4067366430758002
        case 25:
            return 0.42261826174069944
        case 26:
            return 0.4383711467890774
        case 27:
            return 0.45399049973954675
        case 28:
            return 0.4694715627858908
        case 29:
            return 0.48480962024633706
        case 30:
            return 0.49999999999999994
        case 31:
            return 0.5150380749100542
        case 32:
            return 0.5299192642332049
        case 33:
            return 0.5446390350150271
        case 34:
            return 0.5591929034707469
        case 35:
            return 0.573576436351046
        case 36:
            return 0.5877852522924731
        case 37:
            return 0.6018150231520483
        case 38:
            return 0.6156614753256583
        case 39:
            return 0.6293203910498374
        case 40:
            return 0.6427876096865393
        case 41:
            return 0.6560590289905073
        case 42:
            return 0.6691306063588582
        case 43:
            return 0.6819983600624985
        case 44:
            return 0.6946583704589973
        case 45:
            return 0.7071067811865475
        case 46:
            return 0.7193398003386511
        case 47:
            return 0.7313537016191705
        case 48:
            return 0.7431448254773942
        case 49:
            return 0.754709580222772
        case 50:
            return 0.766044443118978
        case 51:
            return 0.7771459614569709
        case 52:
            return 0.788010753606722
        case 53:
            return 0.7986355100472928
        case 54:
            return 0.8090169943749475
        case 55:
            return 0.8191520442889918
        case 56:
            return 0.8290375725550417
        case 57:
            return 0.838670567945424
        case 58:
            return 0.848048096156426
        case 59:
            return 0.8571673007021123
        case 60:
            return 0.8660254037844386
        case 61:
            return 0.8746197071393957
        case 62:
            return 0.8829475928589269
        case 63:
            return 0.8910065241883678
        case 64:
            return 0.898794046299167
        case 65:
            return 0.9063077870366499
        case 66:
            return 0.9135454576426009
        case 67:
            return 0.9205048534524404
        case 68:
            return 0.9271838545667874
        case 69:
            return 0.9335804264972017
        case 70:
            return 0.9396926207859083
        case 71:
            return 0.9455185755993167
        case 72:
            return 0.9510565162951535
        case 73:
            return 0.9563047559630354
        case 74:
            return 0.9612616959383189
        case 75:
            return 0.9659258262890683
        case 76:
            return 0.9702957262759965
        case 77:
            return 0.9743700647852352
        case 78:
            return 0.9781476007338056
        case 79:
            return 0.981627183447664
        case 80:
            return 0.984807753012208
        case 81:
            return 0.9876883405951378
        case 82:
            return 0.9902680687415704
        case 83:
            return 0.992546151641322
        case 84:
            return 0.9945218953682733
        case 85:
            return 0.9961946980917455
        case 86:
            return 0.9975640502598242
        case 87:
            return 0.9986295347545738
        case 88:
            return 0.9993908270190958
        case 89:
            return 0.9998476951563913
        case 90:
            return 1.0
        case 91:
            return 0.9998476951563913
        case 92:
            return 0.9993908270190958
        case 93:
            return 0.9986295347545738
        case 94:
            return 0.9975640502598242
        case 95:
            return 0.9961946980917455
        case 96:
            return 0.9945218953682733
        case 97:
            return 0.9925461516413221
        case 98:
            return 0.9902680687415704
        case 99:
            return 0.9876883405951378
        case 100:
            return 0.984807753012208
        case 101:
            return 0.981627183447664
        case 102:
            return 0.9781476007338057
        case 103:
            return 0.9743700647852352
        case 104:
            return 0.9702957262759965
        case 105:
            return 0.9659258262890683
        case 106:
            return 0.9612616959383189
        case 107:
            return 0.9563047559630355
        case 108:
            return 0.9510565162951536
        case 109:
            return 0.9455185755993168
        case 110:
            return 0.9396926207859084
        case 111:
            return 0.9335804264972017
        case 112:
            return 0.9271838545667874
        case 113:
            return 0.9205048534524403
        case 114:
            return 0.9135454576426009
        case 115:
            return 0.90630778703665
        case 116:
            return 0.8987940462991669
        case 117:
            return 0.8910065241883679
        case 118:
            return 0.8829475928589269
        case 119:
            return 0.8746197071393959
        case 120:
            return 0.8660254037844387
        case 121:
            return 0.8571673007021123
        case 122:
            return 0.8480480961564261
        case 123:
            return 0.8386705679454239
        case 124:
            return 0.8290375725550417
        case 125:
            return 0.8191520442889917
        case 126:
            return 0.8090169943749475
        case 127:
            return 0.7986355100472927
        case 128:
            return 0.788010753606722
        case 129:
            return 0.777145961456971
        case 130:
            return 0.766044443118978
        case 131:
            return 0.7547095802227721
        case 132:
            return 0.7431448254773942
        case 133:
            return 0.7313537016191706
        case 134:
            return 0.7193398003386511
        case 135:
            return 0.7071067811865476
        case 136:
            return 0.6946583704589971
        case 137:
            return 0.6819983600624986
        case 138:
            return 0.6691306063588583
        case 139:
            return 0.6560590289905073
        case 140:
            return 0.6427876096865395
        case 141:
            return 0.6293203910498374
        case 142:
            return 0.6156614753256584
        case 143:
            return 0.6018150231520482
        case 144:
            return 0.5877852522924732
        case 145:
            return 0.5735764363510459
        case 146:
            return 0.5591929034707469
        case 147:
            return 0.5446390350150273
        case 148:
            return 0.5299192642332049
        case 149:
            return 0.5150380749100544
        case 150:
            return 0.49999999999999994
        case 151:
            return 0.48480962024633717
        case 152:
            return 0.4694715627858907
        case 153:
            return 0.45399049973954686
        case 154:
            return 0.4383711467890773
        case 155:
            return 0.4226182617406995
        case 156:
            return 0.40673664307580043
        case 157:
            return 0.39073112848927377
        case 158:
            return 0.37460659341591224
        case 159:
            return 0.3583679495453002
        case 160:
            return 0.3420201433256689
        case 161:
            return 0.3255681544571566
        case 162:
            return 0.3090169943749475
        case 163:
            return 0.2923717047227366
        case 164:
            return 0.2756373558169992
        case 165:
            return 0.258819045102521
        case 166:
            return 0.24192189559966773
        case 167:
            return 0.2249510543438652
        case 168:
            return 0.20791169081775931
        case 169:
            return 0.19080899537654497
        case 170:
            return 0.17364817766693028
        case 171:
            return 0.15643446504023098
        case 172:
            return 0.13917310096006533
        case 173:
            return 0.12186934340514755
        case 174:
            return 0.10452846326765373
        case 175:
            return 0.0871557427476582
        case 176:
            return 0.06975647374412552
        case 177:
            return 0.05233595624294381
        case 178:
            return 0.03489949670250114
        case 179:
            return 0.01745240643728344
        case 180:
            return 1.2246467991473532e-16
        case 181:
            return -0.017452406437283637
        case 182:
            return -0.0348994967025009
        case 183:
            return -0.052335956242943564
        case 184:
            return -0.06975647374412527
        case 185:
            return -0.08715574274765794
        case 186:
            return -0.1045284632676535
        case 187:
            return -0.12186934340514731
        case 188:
            return -0.13917310096006552
        case 189:
            return -0.15643446504023073
        case 190:
            return -0.17364817766693047
        case 191:
            return -0.19080899537654472
        case 192:
            return -0.2079116908177595
        case 193:
            return -0.22495105434386498
        case 194:
            return -0.2419218955996675
        case 195:
            return -0.2588190451025208
        case 196:
            return -0.275637355816999
        case 197:
            return -0.29237170472273677
        case 198:
            return -0.3090169943749473
        case 199:
            return -0.32556815445715676
        case 200:
            return -0.34202014332566866
        case 201:
            return -0.35836794954530043
        case 202:
            return -0.374606593415912
        case 203:
            return -0.39073112848927355
        case 204:
            return -0.4067366430758002
        case 205:
            return -0.4226182617406993
        case 206:
            return -0.43837114678907746
        case 207:
            return -0.4539904997395467
        case 208:
            return -0.46947156278589086
        case 209:
            return -0.48480962024633695
        case 210:
            return -0.5000000000000001
        case 211:
            return -0.5150380749100542
        case 212:
            return -0.5299192642332048
        case 213:
            return -0.5446390350150271
        case 214:
            return -0.5591929034707467
        case 215:
            return -0.5735764363510462
        case 216:
            return -0.587785252292473
        case 217:
            return -0.6018150231520484
        case 218:
            return -0.6156614753256582
        case 219:
            return -0.6293203910498376
        case 220:
            return -0.6427876096865393
        case 221:
            return -0.656059028990507
        case 222:
            return -0.6691306063588582
        case 223:
            return -0.6819983600624984
        case 224:
            return -0.6946583704589974
        case 225:
            return -0.7071067811865475
        case 226:
            return -0.7193398003386512
        case 227:
            return -0.7313537016191705
        case 228:
            return -0.7431448254773944
        case 229:
            return -0.754709580222772
        case 230:
            return -0.7660444431189779
        case 231:
            return -0.7771459614569706
        case 232:
            return -0.7880107536067221
        case 233:
            return -0.7986355100472928
        case 234:
            return -0.8090169943749473
        case 235:
            return -0.8191520442889916
        case 236:
            return -0.8290375725550418
        case 237:
            return -0.838670567945424
        case 238:
            return -0.848048096156426
        case 239:
            return -0.8571673007021121
        case 240:
            return -0.8660254037844384
        case 241:
            return -0.874619707139396
        case 242:
            return -0.882947592858927
        case 243:
            return -0.8910065241883678
        case 244:
            return -0.8987940462991668
        case 245:
            return -0.90630778703665
        case 246:
            return -0.913545457642601
        case 247:
            return -0.9205048534524403
        case 248:
            return -0.9271838545667873
        case 249:
            return -0.9335804264972016
        case 250:
            return -0.9396926207859084
        case 251:
            return -0.9455185755993168
        case 252:
            return -0.9510565162951535
        case 253:
            return -0.9563047559630353
        case 254:
            return -0.961261695938319
        case 255:
            return -0.9659258262890683
        case 256:
            return -0.9702957262759965
        case 257:
            return -0.9743700647852351
        case 258:
            return -0.9781476007338056
        case 259:
            return -0.981627183447664
        case 260:
            return -0.984807753012208
        case 261:
            return -0.9876883405951377
        case 262:
            return -0.9902680687415703
        case 263:
            return -0.9925461516413221
        case 264:
            return -0.9945218953682734
        case 265:
            return -0.9961946980917455
        case 266:
            return -0.9975640502598242
        case 267:
            return -0.9986295347545738
        case 268:
            return -0.9993908270190958
        case 269:
            return -0.9998476951563913
        case 270:
            return -1.0
        case 271:
            return -0.9998476951563913
        case 272:
            return -0.9993908270190958
        case 273:
            return -0.9986295347545738
        case 274:
            return -0.9975640502598243
        case 275:
            return -0.9961946980917455
        case 276:
            return -0.9945218953682734
        case 277:
            return -0.992546151641322
        case 278:
            return -0.9902680687415704
        case 279:
            return -0.9876883405951378
        case 280:
            return -0.9848077530122081
        case 281:
            return -0.9816271834476639
        case 282:
            return -0.9781476007338056
        case 283:
            return -0.9743700647852352
        case 284:
            return -0.9702957262759966
        case 285:
            return -0.9659258262890684
        case 286:
            return -0.9612616959383188
        case 287:
            return -0.9563047559630354
        case 288:
            return -0.9510565162951536
        case 289:
            return -0.945518575599317
        case 290:
            return -0.9396926207859083
        case 291:
            return -0.9335804264972017
        case 292:
            return -0.9271838545667874
        case 293:
            return -0.9205048534524405
        case 294:
            return -0.9135454576426011
        case 295:
            return -0.9063077870366499
        case 296:
            return -0.898794046299167
        case 297:
            return -0.891006524188368
        case 298:
            return -0.8829475928589271
        case 299:
            return -0.8746197071393956
        case 300:
            return -0.8660254037844386
        case 301:
            return -0.8571673007021123
        case 302:
            return -0.8480480961564262
        case 303:
            return -0.8386705679454243
        case 304:
            return -0.8290375725550416
        case 305:
            return -0.8191520442889918
        case 306:
            return -0.8090169943749476
        case 307:
            return -0.798635510047293
        case 308:
            return -0.7880107536067218
        case 309:
            return -0.7771459614569708
        case 310:
            return -0.7660444431189781
        case 311:
            return -0.7547095802227722
        case 312:
            return -0.7431448254773946
        case 313:
            return -0.7313537016191703
        case 314:
            return -0.7193398003386512
        case 315:
            return -0.7071067811865477
        case 316:
            return -0.6946583704589976
        case 317:
            return -0.6819983600624983
        case 318:
            return -0.6691306063588581
        case 319:
            return -0.6560590289905074
        case 320:
            return -0.6427876096865396
        case 321:
            return -0.6293203910498378
        case 322:
            return -0.6156614753256582
        case 323:
            return -0.6018150231520483
        case 324:
            return -0.5877852522924734
        case 325:
            return -0.5735764363510465
        case 326:
            return -0.5591929034707466
        case 327:
            return -0.544639035015027
        case 328:
            return -0.529919264233205
        case 329:
            return -0.5150380749100545
        case 330:
            return -0.5000000000000004
        case 331:
            return -0.4848096202463369
        case 332:
            return -0.4694715627858908
        case 333:
            return -0.45399049973954697
        case 334:
            return -0.4383711467890778
        case 335:
            return -0.4226182617406992
        case 336:
            return -0.40673664307580015
        case 337:
            return -0.3907311284892739
        case 338:
            return -0.37460659341591235
        case 339:
            return -0.35836794954530077
        case 340:
            return -0.3420201433256686
        case 341:
            return -0.3255681544571567
        case 342:
            return -0.3090169943749476
        case 343:
            return -0.29237170472273716
        case 344:
            return -0.27563735581699894
        case 345:
            return -0.2588190451025207
        case 346:
            return -0.24192189559966787
        case 347:
            return -0.22495105434386534
        case 348:
            return -0.20791169081775987
        case 349:
            return -0.19080899537654467
        case 350:
            return -0.1736481776669304
        case 351:
            return -0.15643446504023112
        case 352:
            return -0.13917310096006588
        case 353:
            return -0.12186934340514723
        case 354:
            return -0.10452846326765342
        case 355:
            return -0.08715574274765832
        case 356:
            return -0.06975647374412564
        case 357:
            return -0.05233595624294437
        case 358:
            return -0.034899496702500823
        case 359:
            return -0.01745240643728356
        case 360:
            return -2.4492935982947064e-16
        case _:
            raise ValueError(f"Uncompiled variant angle={angle}")


def main():
    n = 1000000
    random_args = [random.randint(0, 360) for _ in range(n)]

    def run_a_lot():
        for i in range(n):
            precomputed_sine(random_args[i])

    n2 = 10  # better than making 'n' bigger because that takes more memory
    time_taken = timeit.timeit(run_a_lot, number=n2)
    per_run = time_taken / n / n2 * 1000000000.0
    print(
        f"Function executed in: {time_taken:.4f} seconds total; avg of {per_run:.2f} ns. per execution."
    )


if __name__ == "__main__":
    main()

