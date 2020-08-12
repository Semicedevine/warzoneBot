class MME:
    
    #superbonuses_data = (continent id, bonus armies rewarded on capture)
    #regions_data = (region id, continent that it's a part of's id, x coordinates, y coordinates)
    #neighbors_data = (region id, list of the ids of every region that is being neighbored)

    #first superbonus will always be for the regions that don't have superbonuses
    superRegions_data = (0, 0, 1, 5, 2, 5, 3, 5, 4, 3, 5, 4, 6, 3, 7, 5, 8, 3, 9, 4, 10, 4, 11, 3, 12, 5, 13, 3, 14, 4, 15, 4, 16, 5, 17, 4, 18, 5, 19, 6, 20, 4, 21, 3, 22, 4, 23, 5)
    regions_data = (0, 0, 358, 239, 352, 243, 1, 1, 401, 252, 404, 234, 2, 1, 395, 300, 395, 280, 3, 1, 471, 252, 465, 232, 4, 1, 471, 289, 464, 296, 5, 1, 548, 237, 541, 216, 6, 1, 619, 302, 615, 284, 7, 1, 543, 305, 543, 314, 8, 2, 385, 343, 388, 323, 9, 2, 430, 334, 403, 342, 10, 2, 433, 371, 427, 350, 11, 2, 391, 375, 386, 358, 12, 2, 363, 391, 354, 370, 13, 2, 404, 402, 400, 384, 14, 2, 445, 417, 437, 426, 15, 3, 469, 348, 481, 326, 16, 3, 506, 367, 504, 373, 17, 3, 562, 362, 548, 370, 18, 3, 536, 397, 499, 384, 19, 3, 512, 412, 516, 431, 20, 3, 484, 409, 467, 387, 21, 4, 419, 467, 415, 474, 22, 4, 367, 444, 361, 408, 23, 4, 536, 477, 532, 462, 24, 4, 486, 512, 487, 517, 25, 0, 228, 484, 223, 486, 26, 5, 543, 570, 544, 579, 27, 5, 590, 550, 577, 532, 28, 5, 659, 648, 647, 616, 29, 5, 591, 682, 584, 661, 30, 5, 605, 748, 601, 763, 31, 6, 639, 992, 632, 974, 32, 6, 1172, 1006, 1167, 986, 33, 6, 1013, 982, 1008, 963, 34, 6, 1362, 989, 1363, 967, 35, 7, 740, 238, 732, 245, 36, 7, 738, 183, 749, 166, 37, 7, 777, 193, 750, 197, 38, 7, 809, 215, 824, 198, 39, 7, 835, 178, 842, 184, 40, 7, 840, 241, 835, 243, 41, 8, 1017, 747, 1009, 755, 42, 8, 1116, 689, 1108, 702, 43, 8, 992, 706, 974, 713, 44, 8, 1024, 677, 1033, 685, 45, 8, 981, 657, 975, 665, 46, 9, 1011, 605, 1009, 618, 47, 9, 958, 586, 955, 593, 48, 9, 987, 519, 983, 531, 49, 9, 935, 538, 926, 546, 50, 9, 890, 541, 884, 520, 51, 10, 1063, 622, 1053, 601, 52, 10, 1082, 586, 1100, 564, 53, 10, 1084, 542, 1080, 549, 54, 10, 1036, 518, 1034, 493, 55, 10, 1034, 447, 1027, 424, 56, 11, 979, 444, 978, 425, 57, 11, 949, 495, 944, 475, 58, 11, 890, 492, 843, 515, 59, 11, 843, 470, 839, 450, 60, 11, 905, 434, 899, 410, 61, 12, 880, 371, 872, 351, 62, 12, 912, 334, 908, 316, 63, 12, 1001, 350, 998, 332, 64, 12, 897, 300, 887, 282, 65, 12, 943, 310, 940, 317, 66, 12, 979, 312, 982, 321, 67, 12, 1020, 310, 1035, 318, 68, 13, 961, 270, 968, 236, 69, 13, 938, 260, 931, 263, 70, 13, 967, 181, 961, 183, 71, 13, 471, 252, 1000, 229, 72, 14, 1030, 236, 1024, 218, 73, 14, 1037, 270, 1039, 285, 74, 14, 1077, 258, 1077, 269, 75, 14, 1116, 244, 1117, 252, 76, 14, 1125, 293, 1137, 293, 77, 15, 1053, 378, 1045, 359, 78, 15, 1069, 403, 1061, 415, 79, 15, 1115, 470, 1110, 481, 80, 15, 484, 409, 1106, 418, 81, 15, 1147, 412, 1155, 423, 82, 15, 1199, 407, 1190, 413, 83, 16, 1087, 335, 1090, 340, 84, 16, 1137, 329, 1129, 311, 85, 16, 1189, 317, 1186, 325, 86, 16, 1158, 365, 1174, 368, 87, 16, 1218, 366, 1223, 374, 88, 16, 1239, 335, 1233, 315, 89, 17, 1167, 239, 1160, 217, 90, 17, 1183, 280, 1193, 264, 91, 17, 1227, 215, 1224, 225, 92, 17, 1256, 264, 1253, 243, 93, 17, 1243, 293, 1259, 303, 94, 18, 1311, 257, 1305, 231, 95, 18, 1384, 247, 1389, 258, 96, 18, 1375, 301, 1370, 279, 97, 18, 1451, 306, 1432, 282, 98, 18, 1444, 235, 1436, 215, 99, 18, 1519, 238, 1518, 244, 100, 19, 1341, 337, 1327, 317, 101, 19, 1402, 354, 1415, 334, 102, 19, 1453, 337, 1437, 319, 103, 19, 1277, 365, 1272, 343, 104, 19, 1320, 392, 1320, 373, 105, 19, 1286, 412, 1305, 420, 106, 19, 1377, 419, 1374, 400, 107, 20, 1415, 380, 1410, 362, 108, 20, 1419, 424, 1417, 402, 109, 20, 1382, 452, 1409, 457, 110, 20, 1445, 438, 1434, 446, 111, 20, 1466, 466, 1464, 468, 112, 21, 1211, 438, 1220, 413, 113, 21, 1267, 466, 1261, 482, 114, 21, 1333, 458, 1347, 467, 115, 21, 1389, 503, 1379, 480, 116, 22, 1385, 599, 1371, 577, 117, 22, 1444, 588, 1449, 566, 118, 22, 1490, 535, 1479, 514, 119, 22, 1576, 618, 1556, 598, 120, 22, 1660, 638, 1660, 640, 121, 0, 1470, 382, 1460, 363, 122, 0, 1523, 388, 1497, 395, 123, 23, 1555, 703, 1530, 678, 124, 23, 1468, 734, 1461, 746, 125, 23, 1534, 753, 1529, 731, 126, 23, 1582, 751, 1580, 732, 127, 23, 1544, 813, 1542, 815, 128, 23, 1662, 810, 1624, 826)
    neighbors_data = (0, '1 2 99', 1, '2 3', 2, '3 4 9 8', 3, '4 5', 4, '9 15 7 5', 5, '6 36', 6, '7 17 35', 7, '15 16 17', 8, '9 11 12', 9, '15 10 11', 10, '11 13 14 20 15', 11, '13 12', 12, '15 13 22', 13, '14 22 21', 14, '20 21', 15, '20 16', 16, '20 18 17', 17, '18', 18, '20', 19, '20 23', 20, '14', 21, '22 24 23', 23, '27', 24, '26', 25, '122 120', 26, '27 28 30', 27, '28', 28, '30 29 49', 29, '30', 30, '31', 31, '32', 32, '33 34', 33, '41', 34, '127 128', 35, '37 38', 36, '37', 37, '38 39', 38, '39 40', 39, '70', 40, '64', 41, '42 43 44 51', 42, '51', 43, '44 45', 44, '45 46 51', 45, '46', 46, '51 52 54 48 47', 47, '49 48', 48, '49 57 56 54', 50, '57 58', 51, '52', 52, '53 54', 53, '54', 54, '55 56', 55, '56 79 78', 56, '57 60', 57, '58 60', 58, '59 60', 59, '60', 60, '61', 61, '62', 62, '63 64 65', 63, '65 66 67', 64, '65', 65, '66 68', 66, '67', 67, '71 73 83', 68, '69 71', 69, '70 71 72', 71, '72 73', 72, '73 74', 73, '74 76 83', 74, '75 76', 75, '89 76', 76, '89 90 85 84 83', 77, '81 80 78', 78, '80 79', 79, '80', 80, '81', 81, '82 83 112', 83, '84', 84, '85 86', 85, '90 93 88 87 86', 86, '87', 87, '88 112 103', 88, '93 103', 89, '91 90', 90, '91 92 93', 91, '92 94', 92, '93 94', 93, '94 100 103', 94, '95 96 100', 95, '98 97 96', 96, '100 101 97', 97, '98 99 122 102 101', 98, '99', 99, '122', 100, '101 103 104', 101, '102 107 106 104', 102, '107 121', 103, '104 105 112', 104, '105 106', 105, '113 114 109 106', 106, '107 108 109', 107, '108', 108, '110 109', 109, '110 114 115', 110, '111', 111, '118', 112, '113', 113, '114', 114, '115', 115, '116', 116, '117 124', 117, '118 119', 118, '119', 119, '120 123', 121, '122', 123, '124 125 126', 124, '125', 125, '126 127', 126, '128', 127, '128')





"""
#(x, y, number of armies, controlled by...)
    alaska = (72, 119, -1, "unknown")
    attack = (72, 143)
    confirm = (72, 167)

    chat = (90, 848)
    menu = (80, 876)

    cards = (90, 569)
    history = (90, 593)
    settings = (90, 618)
    players = (90, 640)
    surrender = (90, 666)
    vte = (90, 691)
    analyze = (90, 712)
    statistics = (90, 740)
    boot = (90, 761)
    full_screen = (90, 787)
    auto_pilot = (90, 809)
    refresh = (90, 839)
    """