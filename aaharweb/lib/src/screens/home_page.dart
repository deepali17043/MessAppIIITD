import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:fryo/src/screens/appissue_page.dart';
import 'package:fryo/src/screens/signin_page.dart';
import 'package:loader_overlay/loader_overlay.dart';
import 'package:page_transition/page_transition.dart';
import '../shared/styles.dart';
import '../shared/colors.dart';
import '../shared/buttons.dart';
import 'package:fryo/main.dart';
import '../screens/vendor_page.dart';
import '../screens/calendar_page.dart';
import 'package:http/http.dart';
import '../screens/base_page.dart';
import '../shared/vendor.dart';
import '../shared/creds.dart';
import '../screens/messissue_page.dart';
import '../screens/viewissues_page.dart';
import 'package:flutter_easyloading/flutter_easyloading.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../start_page.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';
import 'package:flutter_overlay_loader/flutter_overlay_loader.dart';
import 'package:toggle_bar/toggle_bar.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:ff_navigation_bar/ff_navigation_bar.dart';
import 'package:ndialog/ndialog.dart';

class MarkedDay {
  bool bre = false,
      lun = false,
      sna = false,
      din = false,
      ebre = false,
      elun = false,
      esna = false,
      edin = false;
  MarkedDay();
}

int selectedIndex = 2;

var menuItems = new List.generate(7, (_) => new List<String>(4));

class JsonObj {
  String date;
  List<String> meals;
  JsonObj(this.date, this.meals);
  Map<String, dynamic> toJson() {
    return {
      "date": this.date,
      "meals": this.meals,
    };
  }
}

Future<bool> logout() async {
  Response response = await post(
    url + 'api/logout/',
    headers: {
      'Authorization': userToken,
    },
  );
  final SharedPreferences prefs = await SharedPreferences.getInstance();
  prefs.setString('username', null);
  prefs.setString('password', null);
  name = '';
  password = '';
  isLoggedIn = false;
  print('logout');
  print(response.statusCode);
}

List<MarkedDay> mCalender = [];
List<MarkedDay> oldCalender = [];
List<MarkedDay> nextmCalender = [];
List<MarkedDay> nextoldCalender = [];
bool newMonth = daysRemaining < 7;
bool loading = false;
Future<bool> getUserData() async {
  Response response = await post(
    url + 'api/accounts/home/',
    headers: {
      'Authorization': userToken,
    },
  );
  print('getcoupons');
  print(response.statusCode);
  var userData = jsonDecode(response.body);
  breakCoupon = userData['mess_user']['breakfast_coupons'];
  lunchCoupon = userData['mess_user']['lunch_coupons'];
  snackCoupon = userData['mess_user']['snacks_coupons'];
  dinnerCoupon = userData['mess_user']['dinner_coupons'];
}

Future<List<MarkedDay>> getCalendar() async {
  List<MarkedDay> tCalender = [];

  Response response = await post(
    url + 'api/accounts/schedule/',
    headers: {
      'Authorization': userToken,
    },
  );
  print('ooo');
  print(response.body);
  int adj = DateTime.now().day;

  List decode = jsonDecode(response.body)['attendance'];
  tCalender.add(new MarkedDay());
  for (int i = 1; i <= monthDays[DateTime.now().month - 1]; i++) {
    tCalender.add(new MarkedDay());
    if (i >= DateTime.now().day && i < DateTime.now().day + 7) {
      tCalender[i].bre = decode[(i - adj) * 4]['attending'];
      tCalender[i].lun = decode[(i - adj) * 4 + 1]['attending'];
      tCalender[i].sna = decode[(i - adj) * 4 + 2]['attending'];
      tCalender[i].din = decode[(i - adj) * 4 + 3]['attending'];
      tCalender[i].ebre = decode[(i - adj) * 4]['editable'];
      tCalender[i].elun = decode[(i - adj) * 4 + 1]['editable'];
      tCalender[i].esna = decode[(i - adj) * 4 + 2]['editable'];
      tCalender[i].edin = decode[(i - adj) * 4 + 3]['editable'];
    }
  }
  int j = 1;
  for (int i = 0; i < 32; i++) {
    nextoldCalender.add(new MarkedDay());
  }
  for (int i = 0; i < decode.length;) {
    int montt = int.parse(decode[i]['date'].toString().substring(5, 7));
    if (montt > DateTime.now().month) {
      nextoldCalender[j].bre = decode[i]['attending'];
      nextoldCalender[j].lun = decode[i + 1]['attending'];
      nextoldCalender[j].sna = decode[i + 2]['attending'];
      nextoldCalender[j].din = decode[i + 3]['attending'];
      nextoldCalender[j].ebre = decode[i]['editable'];
      nextoldCalender[j].elun = decode[i + 1]['editable'];
      nextoldCalender[j].esna = decode[i + 2]['editable'];
      nextoldCalender[j].edin = decode[i + 3]['editable'];
      j++;
      i += 4;
    } else {
      i++;
    }
  }
  print(nextoldCalender[1].esna);

  print('get');
  return tCalender;
//  print(response.body);
}

Future<void> updateCalendar() async {
  List<JsonObj> jsonCalendar = [];
  for (int i = 0; i <= monthDays[DateTime.now().month - 1]; i++) {
    String date = currentYear.toString() +
        '-' +
        DateTime.now().month.toString().padLeft(2, '0') +
        '-' +
        i.toString().padLeft(2, '0');
    List<String> meals = [];
    if (mCalender[i].bre != oldCalender[i].bre) {
      meals.add('Breakfast');
    }
    if (mCalender[i].lun != oldCalender[i].lun) {
      meals.add('Lunch');
    }
    if (mCalender[i].sna != oldCalender[i].sna) {
      meals.add('Snacks');
    }
    if (mCalender[i].din != oldCalender[i].din) {
      meals.add('Dinner');
    }
    JsonObj json = new JsonObj(date, meals);
    //  print(meals);
    if (meals.length > 0) {
      jsonCalendar.add(json);
    }
  }
  for (int i = 0; i <= 7; i++) {
    String date = currentYear.toString() +
        '-' +
        (DateTime.now().month + 1).toString().padLeft(2, '0') +
        '-' +
        i.toString().padLeft(2, '0');
    List<String> meals = [];
    if (nextmCalender[i].bre != nextoldCalender[i].bre) {
      meals.add('Breakfast');
    }
    if (nextmCalender[i].lun != nextoldCalender[i].lun) {
      meals.add('Lunch');
    }
    if (nextmCalender[i].sna != nextoldCalender[i].sna) {
      meals.add('Snacks');
    }
    if (nextmCalender[i].din != nextoldCalender[i].din) {
      meals.add('Dinner');
    }
    JsonObj json = new JsonObj(date, meals);
    //  print(meals);
    if (meals.length > 0) {
      jsonCalendar.add(json);
    }
  }
  String encoded = jsonEncode(jsonCalendar);
  print('edit meals');
  print(encoded);
  Response response = await post(
    url + 'api/accounts/schedule/edit/',
    headers: {
      'Authorization': userToken,
      'attendance': encoded,
      'Content-Type': 'application/json; charset=UTF-8',
    },
  );

  print('edit response');
  print(response.body);
}

Future<void> getMessMenu() async {
  Response response = await post(
    url + 'api/accounts/weekly-menu/',
    headers: {
      'Authorization': userToken,
    },
  );
  List decode = jsonDecode(response.body)['weekly_menu'];
  for (int i = 0; i < decode.length; i++) {
    if (decode[i]["day"] == "Monday") {
      if (decode[i]["meal"] == "Breakfast") {
        menuItems[0][0] = decode[i]["items"];
      } else if (decode[i]["meal"] == "Lunch") {
        menuItems[0][1] = decode[i]["items"];
      } else if (decode[i]["meal"] == "Snacks") {
        menuItems[0][2] = decode[i]["items"];
      } else if (decode[i]["meal"] == "Dinner") {
        menuItems[0][3] = decode[i]["items"];
      }
    } else if (decode[i]["day"] == "Tuesday") {
      if (decode[i]["meal"] == "Breakfast") {
        menuItems[1][0] = decode[i]["items"];
      } else if (decode[i]["meal"] == "Lunch") {
        menuItems[1][1] = decode[i]["items"];
      } else if (decode[i]["meal"] == "Snacks") {
        menuItems[1][2] = decode[i]["items"];
      } else if (decode[i]["meal"] == "Dinner") {
        menuItems[1][3] = decode[i]["items"];
      }
    } else if (decode[i]["day"] == "Wednesday") {
      if (decode[i]["meal"] == "Breakfast") {
        menuItems[2][0] = decode[i]["items"];
      } else if (decode[i]["meal"] == "Lunch") {
        menuItems[2][1] = decode[i]["items"];
      } else if (decode[i]["meal"] == "Snacks") {
        menuItems[2][2] = decode[i]["items"];
      } else if (decode[i]["meal"] == "Dinner") {
        menuItems[2][3] = decode[i]["items"];
      }
    } else if (decode[i]["day"] == "Thursday") {
      if (decode[i]["meal"] == "Breakfast") {
        menuItems[3][0] = decode[i]["items"];
      } else if (decode[i]["meal"] == "Lunch") {
        menuItems[3][1] = decode[i]["items"];
      } else if (decode[i]["meal"] == "Snacks") {
        menuItems[3][2] = decode[i]["items"];
      } else if (decode[i]["meal"] == "Dinner") {
        menuItems[3][3] = decode[i]["items"];
      }
    } else if (decode[i]["day"] == "Friday") {
      if (decode[i]["meal"] == "Breakfast") {
        menuItems[4][0] = decode[i]["items"];
      } else if (decode[i]["meal"] == "Lunch") {
        menuItems[4][1] = decode[i]["items"];
      } else if (decode[i]["meal"] == "Snacks") {
        menuItems[4][2] = decode[i]["items"];
      } else if (decode[i]["meal"] == "Dinner") {
        menuItems[4][3] = decode[i]["items"];
      }
    } else if (decode[i]["day"] == "Saturday") {
      if (decode[i]["meal"] == "Breakfast") {
        menuItems[5][0] = decode[i]["items"];
      } else if (decode[i]["meal"] == "Lunch") {
        menuItems[0][1] = decode[i]["items"];
      } else if (decode[i]["meal"] == "Snacks") {
        menuItems[5][2] = decode[i]["items"];
      } else if (decode[i]["meal"] == "Dinner") {
        menuItems[5][3] = decode[i]["items"];
      }
    } else if (decode[i]["day"] == "Sunday") {
      if (decode[i]["meal"] == "Breakfast") {
        menuItems[6][0] = decode[i]["items"];
      } else if (decode[i]["meal"] == "Lunch") {
        menuItems[6][1] = decode[i]["items"];
      } else if (decode[i]["meal"] == "Snacks") {
        menuItems[6][2] = decode[i]["items"];
      } else if (decode[i]["meal"] == "Dinner") {
        menuItems[6][3] = decode[i]["items"];
      }
    }
  }
  print(decode);
}

class HomePage extends StatefulWidget {
  final String pageTitle;
  int bfc, lnc, snc, dnc;
  HomePage({Key key, this.pageTitle}) : super(key: key);

  @override
  _HomePageState createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  bool yesButton = true;
  List<String> labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  List<String> meals = ["", "", ""];
  int mealIndex = 0;
  int currentIndex = 0;
  Color mealColor = Colors.blueGrey.shade50;
  Color mealColorH = primaryColor;

  @override
  void initState() {
    super.initState();
    Loader.show(
      context,
      progressIndicator: CircularProgressIndicator(
        backgroundColor: Colors.white,
      ),
    );

    getMessMenu();

    // getUserData().then((value) {
    //   setState(() {
    //     widget.bfc = breakCoupon;
    //     widget.lnc = lunchCoupon;
    //     widget.snc = snackCoupon;
    //     widget.dnc = dinnerCoupon;
    //   });
    // });
    for (int i = 0; i < 32; i++) {
      mCalender.add(new MarkedDay());
    }
    getCalendar().then((value) {
      setState(() {
        mCalender = List.from(value);
        for (int i = 0; i < mCalender.length; i++) {
          oldCalender.add(new MarkedDay());
          oldCalender[i].bre = mCalender[i].bre;
          oldCalender[i].lun = mCalender[i].lun;
          oldCalender[i].sna = mCalender[i].sna;
          oldCalender[i].din = mCalender[i].din;
          oldCalender[i].ebre = mCalender[i].ebre;
          oldCalender[i].elun = mCalender[i].elun;
          oldCalender[i].esna = mCalender[i].esna;
          oldCalender[i].edin = mCalender[i].edin;
        }
      });
      for (int i = 0; i < nextoldCalender.length; i++) {
        nextmCalender.add(new MarkedDay());
        nextmCalender[i].bre = nextoldCalender[i].bre;
        nextmCalender[i].lun = nextoldCalender[i].lun;
        nextmCalender[i].sna = nextoldCalender[i].sna;
        nextmCalender[i].din = nextoldCalender[i].din;
        nextmCalender[i].ebre = nextoldCalender[i].ebre;
        nextmCalender[i].elun = nextoldCalender[i].elun;
        nextmCalender[i].esna = nextoldCalender[i].esna;
        nextmCalender[i].edin = nextoldCalender[i].edin;
      }
      selectedIndex = 2;
      Loader.hide();
    });
    print('init');
  }

  DateTime currentBackPressTime;

  Future<bool> onWillPop() {
    DateTime now = DateTime.now();
    if (currentBackPressTime == null ||
        now.difference(currentBackPressTime) > Duration(seconds: 3)) {
      currentBackPressTime = now;
      EasyLoading.showToast('Press back again to exit');
      return Future.value(false);
    }
    return Future.value(true);
  }

  _launchURL() async {
    const url =
        'https://docs.google.com/forms/d/e/1FAIpQLSeANRTqSIeUqdbLpV5wq-E8Hp5BsPj1VAsmPyr3whVYFGShWw/viewform';
    if (await canLaunch(url)) {
      await launch(url);
    } else {
      throw 'Could not launch $url';
    }
  }

  @override
  Widget build(BuildContext context) {
    return WillPopScope(
        onWillPop: onWillPop,
        child: LoaderOverlay(
          overlayWidget: Center(
            child: SpinKitCubeGrid(
              color: Colors.red,
              size: 50.0,
            ),
          ),
          overlayOpacity: 0.8,
          child: Scaffold(
            backgroundColor: bgColor,
            appBar: AppBar(
              centerTitle: true,
              elevation: 0,
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(20)),
              backgroundColor: white,
              title: Text('Home Page', style: h3, textAlign: TextAlign.center),
            ),
            body: Column(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: <Widget>[
                Padding(
                  padding: const EdgeInsets.all(0.0),
                  child: Column(
                    children: <Widget>[
                      Container(
                        width: double.infinity,
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.all(Radius.circular(20.0)),
                          //
                        ),
                        child: Padding(
                          padding: const EdgeInsets.only(bottom: 8.0),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.center,
                            children: [
                              Align(
                                alignment: Alignment.centerLeft,
                                child: ToggleBar(
                                  labels: labels,
                                  backgroundColor: Colors.white,
                                  selectedTabColor: primaryColor,
                                  selectedTextColor: Colors.white,
                                  textColor: Colors.black,
                                  onSelectionUpdated: (index) =>
                                      setState(() => currentIndex = index),
                                ),
                              ),
                              Container(
                                height: 80,
                                padding: EdgeInsets.all(5),
                                child: Row(
                                  children: [
                                    Expanded(
                                      child: GestureDetector(
                                        onTap: () {
                                          setState(() {
                                            mealIndex = 0;
                                          });
                                        },
                                        child: Container(
                                          padding: EdgeInsets.all(4),
                                          //         width: 150,

                                          margin: EdgeInsets.all(2),
                                          decoration: BoxDecoration(
                                            color: mealIndex == 0
                                                ? mealColorH
                                                : mealColor,
                                            borderRadius: BorderRadius.all(
                                                Radius.circular(20.0)),
                                            //
                                          ),
                                          alignment: Alignment.center,
                                          child: Text(
                                            "Breakfast",
                                            style: mealIndex == 0 ? h9w : h9b,
                                          ),
                                        ),
                                      ),
                                    ),
                                    Expanded(
                                      child: GestureDetector(
                                        onTap: () {
                                          setState(() {
                                            mealIndex = 1;
                                          });
                                        },
                                        child: Container(
                                          padding: EdgeInsets.all(4),
                                          //     width: 150,
                                          margin: EdgeInsets.all(2),
                                          decoration: BoxDecoration(
                                            color: mealIndex == 1
                                                ? mealColorH
                                                : mealColor,
                                            borderRadius: BorderRadius.all(
                                                Radius.circular(20.0)),
                                            //
                                          ),
                                          alignment: Alignment.center,

                                          child: Text(
                                            "Lunch",
                                            style: mealIndex == 1 ? h9w : h9b,
                                          ),
                                        ),
                                      ),
                                    ),
                                    menuItems[currentIndex][2] != null
                                        ? Expanded(
                                            child: GestureDetector(
                                              onTap: () {
                                                setState(() {
                                                  mealIndex = 2;
                                                });
                                              },
                                              child: Container(
                                                padding: EdgeInsets.all(4),
                                                margin: EdgeInsets.all(2),
                                                decoration: BoxDecoration(
                                                  color: mealIndex == 2
                                                      ? mealColorH
                                                      : mealColor,
                                                  borderRadius:
                                                      BorderRadius.all(
                                                          Radius.circular(
                                                              20.0)),
                                                  //
                                                ),
                                                alignment: Alignment.center,
                                                child: menuItems[currentIndex]
                                                            [2] !=
                                                        null
                                                    ? Text(
                                                        "Snacks",
                                                        style: mealIndex == 2
                                                            ? h9w
                                                            : h9b,
                                                      )
                                                    : SizedBox(),
                                              ),
                                            ),
                                          )
                                        : SizedBox(),
                                    Expanded(
                                      child: GestureDetector(
                                        onTap: () {
                                          setState(() {
                                            mealIndex = 3;
                                          });
                                        },
                                        child: Container(
                                          padding: EdgeInsets.all(4),
                                          //      width: 150,
                                          margin: EdgeInsets.all(2),
                                          decoration: BoxDecoration(
                                            color: mealIndex == 3
                                                ? mealColorH
                                                : mealColor,
                                            borderRadius: BorderRadius.all(
                                                Radius.circular(20.0)),
                                            //
                                          ),
                                          alignment: Alignment.center,

                                          child: Text(
                                            "Dinner",
                                            style: mealIndex == 3 ? h9w : h9b,
                                          ),
                                        ),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                              Container(
                                padding: EdgeInsets.all(20),
                                width: double.infinity,
                                margin: EdgeInsets.all(3),
                                decoration: BoxDecoration(
                                  color: mealColor,
                                  borderRadius:
                                      BorderRadius.all(Radius.circular(20.0)),
                                  //
                                ),
                                child: Column(
                                  children: [
                                    Text(
                                      menuItems[currentIndex][mealIndex] != null
                                          ? menuItems[currentIndex][mealIndex]
                                          : "",
                                      style: h9,
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),

                      SizedBox(
                        height: 10,
                      ),
                      // Container(
                      //   decoration: BoxDecoration(
                      //     color: Colors.white,
                      //     borderRadius: BorderRadius.all(Radius.circular(30.0)),
                      //   ),
                      //   width: double.infinity,
                      //   child: Column(
                      //     children: [
                      //       Text(
                      //         'Schedule your meals',
                      //         style: h5,
                      //       ),
                      //       IconButton(
                      //         iconSize: 32,
                      //         icon: Icon(Icons.calendar_today),
                      //         color: primaryColor,
                      //         onPressed: () {
                      //           Navigator.push(
                      //                   context,
                      //                   PageTransition(
                      //                       type:
                      //                           PageTransitionType.rightToLeft,
                      //                       child: CalendarPage(
                      //                           //  link to the project at - https://pub.dev/packages/calendarro
                      //                           )))
                      //               .then((value) {
                      //             setState(() {});
                      //           });
                      //         },
                      //       ),
                      //     ],
                      //   ),
                      // ),

                      // Align(
                      //   alignment: Alignment.center,
                      //   child: Text(
                      //     'Remaining coupons for the month',
                      //     style: h5,
                      //     textAlign: TextAlign.end,
                      //   ),
                      // ),
                      // Padding(
                      //   padding: EdgeInsets.all(2),
                      //   child: Row(
                      //     children: <Widget>[
                      //       Expanded(
                      //         child: Card(
                      //           child: Padding(
                      //             padding: const EdgeInsets.all(6.0),
                      //             child: Column(
                      //               children: <Widget>[
                      //                 Text(
                      //                   'Breakfast',
                      //                   style: h7,
                      //                   textAlign: TextAlign.end,
                      //                 ),
                      //                 Text(
                      //                   widget.bfc.toString(),
                      //                   style: h7,
                      //                   textAlign: TextAlign.end,
                      //                 ),
                      //               ],
                      //             ),
                      //           ),
                      //         ),
                      //       ),
                      //       Expanded(
                      //         child: Card(
                      //           child: Padding(
                      //             padding: const EdgeInsets.all(6.0),
                      //             child: Column(
                      //               children: <Widget>[
                      //                 Text(
                      //                   'Lunch',
                      //                   style: h7,
                      //                   textAlign: TextAlign.end,
                      //                 ),
                      //                 Text(
                      //                   widget.lnc.toString(),
                      //                   style: h7,
                      //                   textAlign: TextAlign.end,
                      //                 ),
                      //               ],
                      //             ),
                      //           ),
                      //         ),
                      //       ),
                      //       Expanded(
                      //         child: Card(
                      //           child: Padding(
                      //             padding: const EdgeInsets.all(6.0),
                      //             child: Column(
                      //               children: <Widget>[
                      //                 Text(
                      //                   'Snacks',
                      //                   style: h7,
                      //                   textAlign: TextAlign.end,
                      //                 ),
                      //                 Text(
                      //                   widget.snc.toString(),
                      //                   style: h7,
                      //                   textAlign: TextAlign.end,
                      //                 ),
                      //               ],
                      //             ),
                      //           ),
                      //         ),
                      //       ),
                      //       Expanded(
                      //         child: Card(
                      //           child: Padding(
                      //             padding: const EdgeInsets.all(6.0),
                      //             child: Column(
                      //               children: <Widget>[
                      //                 Text(
                      //                   'Dinner',
                      //                   style: h7,
                      //                   textAlign: TextAlign.end,
                      //                 ),
                      //                 Text(
                      //                   widget.dnc.toString(),
                      //                   style: h7,
                      //                   textAlign: TextAlign.end,
                      //                 ),
                      //               ],
                      //             ),
                      //           ),
                      //         ),
                      //       ),
                      //     ],
                      //   ),
                      // ),
                      SizedBox(
                        height: 20,
                      ),

                      Container(
                        decoration: BoxDecoration(
                          //        color: Colors.green.shade100,
                          borderRadius: BorderRadius.all(Radius.circular(30.0)),
                        ),
                        width: double.infinity,
                        child: Column(
                          children: [
                            Text(
                              'Coming up',
                              style: h5,
                            ),
                            DayView(
                              date: DateTime.now().day,
                            ),
                            DayView(
                              date:
                                  DateTime.now().add(new Duration(days: 1)).day,
                            ),
                            DayView(
                              date:
                                  DateTime.now().add(new Duration(days: 2)).day,
                            )
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                // Column(
                //   children: <Widget>[
                //     Row(
                //       mainAxisAlignment: MainAxisAlignment.center,
                //       children: <Widget>[
                //         Container(
                //           width: 160,
                //           margin: EdgeInsets.all(3),
                //           child: mFlatBtn(
                //               text: 'Mess Feedback',
                //               onPressed: () {
                //                 Navigator.push(
                //                     context,
                //                     PageTransition(
                //                         type: PageTransitionType.rightToLeft,
                //                         child: IssuePage()));
                //               }),
                //         ),
                //         Container(
                //           width: 160,
                //           margin: EdgeInsets.all(3),
                //           child: mFlatBtn(
                //               text: 'Check Feedback Status',
                //               onPressed: () {
                //                 Navigator.push(
                //                     context,
                //                     PageTransition(
                //                         type: PageTransitionType.rightToLeft,
                //                         child: ViewIssuePage()));
                //               }),
                //         ),
                //       ],
                //     ),
                //     Row(
                //       mainAxisAlignment: MainAxisAlignment.center,
                //       children: [
                //         Container(
                //           width: 160,
                //           margin: EdgeInsets.all(3),
                //           child: mFlatBtn(
                //               text: 'App Feedback',
                //               onPressed: () {
                //                 _launchURL();
                //               }),
                //         ),
                //         Container(
                //           width: 160,
                //           margin: EdgeInsets.all(3),
                //           child: mFlatBtn(text: 'Logout', onPressed: () {}),
                //         ),
                //       ],
                //     ),
                //   ],
                // ),
              ],
            ),
            bottomNavigationBar: FFNavigationBar(
              theme: FFNavigationBarTheme(
                barBackgroundColor: Colors.white,
                selectedItemBorderColor: Colors.yellow.shade300,
                selectedItemBackgroundColor: primaryColor,
                selectedItemIconColor: Colors.white,
                selectedItemLabelColor: Colors.black,
              ),
              selectedIndex: selectedIndex,
              onSelectTab: (index) async {
                setState(() {
                  selectedIndex = index;
                });
                if (index == 0) {
                  selectedIndex = 2;
                  final value = await Navigator.push(
                      context,
                      PageTransition(
                          type: PageTransitionType.rightToLeft,
                          child: CalendarPage(
                              //  link to the project at - https://pub.dev/packages/calendarro
                              )));
                  setState(() {
                    mCalender = mCalender;
                  });
                } else if (index == 1) {
                  selectedIndex = 2;
                  await NDialog(
                    dialogStyle: DialogStyle(
                      titleDivider: true,
                    ),
                    actions: <Widget>[
                      FlatButton(
                          child: Text("Raise Mess Issue"),
                          onPressed: () {
                            Navigator.pop(context);
                            Navigator.push(
                                context,
                                PageTransition(
                                    type: PageTransitionType.rightToLeft,
                                    child: MessIssuePage()));
                            setState(() {
                              mCalender = mCalender;
                            });
                          }),
                      FlatButton(
                          child: Text("Raise App Issue"),
                          onPressed: () {
                            Navigator.pop(context);
                            Navigator.push(
                                context,
                                PageTransition(
                                    type: PageTransitionType.rightToLeft,
                                    child: AppIssuePage()));
                          }),
                    ],
                  ).show(
                    context,
                  );
                } else if (index == 2) {
                } else if (index == 3) {
                  selectedIndex = 2;
                  Navigator.push(
                      context,
                      PageTransition(
                          type: PageTransitionType.rightToLeft,
                          child: ViewIssuePage()));
                } else if (index == 4) {
                  selectedIndex = 2;

                  await NDialog(
                    dialogStyle: DialogStyle(
                      titleDivider: true,
                    ),
                    title: Text("Are you sure you want to logout?"),
                    actions: <Widget>[
                      FlatButton(
                          child: Text("Yes"),
                          onPressed: () {
                            Navigator.pop(context);
                            logout().then((value) {
                              //    userToken = '';
                            });
                            Navigator.pushReplacement(
                                context,
                                PageTransition(
                                    type: PageTransitionType.rightToLeft,
                                    child: SignInPage()));
                          }),
                      FlatButton(
                          child: Text("No"),
                          onPressed: () {
                            Navigator.pop(context);
                          }),
                    ],
                  ).show(
                    context,
                  );
                }
              },
              items: [
                FFNavigationBarItem(
                  iconData: Icons.calendar_today,
                  label: 'Schedule',
                ),
                FFNavigationBarItem(
                  iconData: Icons.feedback,
                  label: 'Raise Issue',
                ),
                FFNavigationBarItem(
                  iconData: Icons.home,
                  label: 'Home',
                ),
                FFNavigationBarItem(
                  iconData: Icons.note,
                  label: 'Issue Status',
                ),
                FFNavigationBarItem(
                  iconData: Icons.logout,
                  label: 'Logout',
                ),
              ],
            ),
          ),
        ));
  }
}

class DayView extends StatefulWidget {
  int date;

  DayView({this.date});

  @override
  State<StatefulWidget> createState() {
    // TODO: implement createState
    return DayViewPage(date: this.date);
    throw UnimplementedError();
  }
}

class DayViewPage extends State<DayView> {
  int date;
  DayViewPage({this.date});

  @override
  Widget build(BuildContext context) {
    // TODO: implement build
    MarkedDay mday;

    if (newMonth && date < 4) {
      mday = nextmCalender[date];
    } else {
      mday = mCalender[date];
    }

    return Row(
      children: [
        Container(
          width: 30,
          child: Padding(
            padding: const EdgeInsets.all(5),
            child: Text(
              date.toString(),
              style: h7,
            ),
          ),
        ),
        Expanded(
          child: GestureDetector(
            onTap: () {
              if (newMonth && date < 4) {
                if (nextmCalender[date].ebre) {
                  setState(() {
                    Loader.show(
                      context,
                      progressIndicator: CircularProgressIndicator(
                        backgroundColor: Colors.white,
                      ),
                    );
                    nextmCalender[date].bre = !nextmCalender[date].bre;
                    updateCalendar().then((value) {
                      nextoldCalender[date].bre = !nextoldCalender[date].bre;
                      Loader.hide();
                    });
                  });
                } else {
                  EasyLoading.showToast('Cannot be changed');
                }
              } else {
                if (mCalender[date].ebre) {
                  setState(() {
                    Loader.show(
                      context,
                      progressIndicator: CircularProgressIndicator(
                        backgroundColor: Colors.white,
                      ),
                    );
                    mCalender[date].bre = !mCalender[date].bre;
                    updateCalendar().then((value) {
                      oldCalender[date].bre = !oldCalender[date].bre;
                      Loader.hide();
                    });
                  });
                } else {
                  EasyLoading.showToast('Cannot be changed');
                }
              }
            },
            child: Card(
              color: mday.bre ? primaryColor : Colors.white,
              child: Padding(
                padding: const EdgeInsets.only(
                    left: 3.0, right: 3, top: 4, bottom: 4),
                child: Text(
                  'Breakfast',
                  style: TextStyle(
                      color: mday.bre ? Colors.white : Colors.black,
                      fontSize: 14),
                ),
              ),
            ),
          ),
        ),
        Expanded(
          child: GestureDetector(
            onTap: () {
              if (newMonth && date < 4) {
                if (nextmCalender[date].elun) {
                  setState(() {
                    Loader.show(
                      context,
                      progressIndicator: CircularProgressIndicator(
                        backgroundColor: Colors.white,
                      ),
                    );
                    nextmCalender[date].lun = !nextmCalender[date].lun;
                    updateCalendar().then((value) {
                      nextoldCalender[date].lun = !nextoldCalender[date].lun;
                      Loader.hide();
                    });
                  });
                } else {
                  EasyLoading.showToast('Cannot be changed');
                }
              } else {
                if (mCalender[date].elun) {
                  setState(() {
                    Loader.show(
                      context,
                      progressIndicator: CircularProgressIndicator(
                        backgroundColor: Colors.white,
                      ),
                    );
                    mCalender[date].lun = !mCalender[date].lun;
                    updateCalendar().then((value) {
                      oldCalender[date].lun = !oldCalender[date].lun;
                      Loader.hide();
                    });
                  });
                } else {
                  EasyLoading.showToast('Cannot be changed');
                }
              }
            },
            child: Card(
              color: mday.lun ? primaryColor : Colors.white,
              child: Padding(
                padding: const EdgeInsets.only(
                    left: 3.0, right: 3, top: 4, bottom: 4),
                child: Text(
                  'Lunch',
                  style: TextStyle(
                      color: mday.lun ? Colors.white : Colors.black,
                      fontSize: 14),
                ),
              ),
            ),
          ),
        ),
        Expanded(
          child: GestureDetector(
            onTap: () {
              if (newMonth && date < 4) {
                if (nextmCalender[date].esna) {
                  setState(() {
                    Loader.show(
                      context,
                      progressIndicator: CircularProgressIndicator(
                        backgroundColor: Colors.white,
                      ),
                    );
                    nextmCalender[date].sna = !nextmCalender[date].sna;
                    updateCalendar().then((value) {
                      nextoldCalender[date].sna = !nextoldCalender[date].sna;
                      Loader.hide();
                    });
                  });
                } else {
                  EasyLoading.showToast('Cannot be changed');
                }
              } else {
                if (mCalender[date].esna) {
                  setState(() {
                    Loader.show(
                      context,
                      progressIndicator: CircularProgressIndicator(
                        backgroundColor: Colors.white,
                      ),
                    );
                    mCalender[date].sna = !mCalender[date].sna;
                    updateCalendar().then((value) {
                      oldCalender[date].sna = !oldCalender[date].sna;
                      Loader.hide();
                    });
                  });
                } else {
                  EasyLoading.showToast('Cannot be changed');
                }
              }
            },
            child: Card(
              color: mday.sna ? primaryColor : Colors.white,
              child: Padding(
                padding: const EdgeInsets.only(
                    left: 3.0, right: 3, top: 4, bottom: 4),
                child: Text(
                  'Snacks',
                  style: TextStyle(
                      color: mday.sna ? Colors.white : Colors.black,
                      fontSize: 14),
                ),
              ),
            ),
          ),
        ),
        Expanded(
          child: GestureDetector(
            onTap: () {
              if (newMonth && date < 4) {
                if (nextmCalender[date].edin) {
                  setState(() {
                    Loader.show(
                      context,
                      progressIndicator: CircularProgressIndicator(
                        backgroundColor: Colors.white,
                      ),
                    );
                    nextmCalender[date].din = !nextmCalender[date].din;
                    updateCalendar().then((value) {
                      nextoldCalender[date].din = !nextoldCalender[date].din;
                      Loader.hide();
                    });
                  });
                } else {
                  EasyLoading.showToast('Cannot be changed');
                }
              } else {
                if (mCalender[date].edin) {
                  setState(() {
                    Loader.show(
                      context,
                      progressIndicator: CircularProgressIndicator(
                        backgroundColor: Colors.white,
                      ),
                    );
                    mCalender[date].din = !mCalender[date].din;
                    updateCalendar().then((value) {
                      oldCalender[date].din = !oldCalender[date].din;
                      Loader.hide();
                    });
                  });
                } else {
                  EasyLoading.showToast('Cannot be changed');
                }
              }
            },
            child: Card(
              color: mday.din ? primaryColor : Colors.white,
              child: Padding(
                padding: const EdgeInsets.only(
                    left: 3.0, right: 3, top: 4, bottom: 4),
                child: Text(
                  'Dinner',
                  style: TextStyle(
                      color: mday.din ? Colors.white : Colors.black,
                      fontSize: 14),
                ),
              ),
            ),
          ),
        ),
      ],
    );
    throw UnimplementedError();
  }
}
