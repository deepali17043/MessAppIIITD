import 'dart:async';
import 'dart:convert';
import 'package:ff_navigation_bar/ff_navigation_bar.dart';

import 'package:flutter/material.dart';
import 'package:flutter_easyloading/flutter_easyloading.dart';
import 'package:flutter_overlay_loader/flutter_overlay_loader.dart';
import 'package:fryo/src/screens/signin_page.dart';
import 'package:page_transition/page_transition.dart';
import '../shared/styles.dart';
import '../shared/colors.dart';
import '../shared/buttons.dart';
import '../screens/vendor_page.dart';
import '../screens/home_page.dart';
import 'package:calendarro/date_utils.dart' as cd;
import 'package:calendarro/calendarro.dart';
import 'package:http/http.dart';

List<String> months = [
  'January',
  'February',
  'March',
  'April',
  'May',
  'June',
  'July',
  'August',
  'September',
  'October',
  'Novemeber',
  'December'
];
List<int> monthDays = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
List<String> weekShort = ['M', 'T', 'W', 'T', 'F', 'S', 'S'];

bool isSwitched = false;
bool bfButton = false;
bool lunButton = false;
bool snackButton = false;
bool dinnerButton = false;
int breakCoupon = 0;
int lunchCoupon = 0;
int snackCoupon = 0;
int dinnerCoupon = 0;
int couponsBought = 20;
int currentMonth = monthDays[DateTime.now().month - 1];
int currentYear = DateTime.now().year;

int adj = currentMonth - couponsBought;
int daysRemaining = (monthDays[DateTime.now().month] - DateTime.now().day + 1);
Set<int> multiDates = {};
bool nextMonth = false;
int curDay = DateTime.now().day;

class CalendarPage extends StatefulWidget {
  List<MarkedDay> stateCalendar;
  CalendarPage({Key key}) : super(key: key);

  @override
  _CalendarPageState createState() => _CalendarPageState();
}

class _CalendarPageState extends State<CalendarPage> {
  @override
  Widget build(BuildContext context) {
    callback() {
      setState(() {});
    }

    var startDate = DateTime.now();
    var endDate = startDate.add(new Duration(days: 6));
    var monthCalendarro = Calendarro(
        startDate: startDate,
        endDate: endDate,
        selectedSingleDate: DateTime.now(),
        dayTileBuilder: DaysViewTileBuilder(callback),
        displayMode: DisplayMode.MONTHS,
        selectionMode: isSwitched ? SelectionMode.MULTI : SelectionMode.SINGLE,
        weekdayLabelsRow: CustomWeekdayLabelsRow(),
        onTap: (date) {});

    var nextMonthCalendarro = Calendarro(
        startDate: startDate.add(new Duration(days: (daysRemaining + 1) % 7)),
        endDate: startDate.add(new Duration(days: newMonth ? 6 : 8)),
        selectedSingleDate:
            startDate.add(new Duration(days: daysRemaining + 1)),
        dayTileBuilder: DaysViewTileBuilder(callback),
        displayMode: DisplayMode.MONTHS,
        selectionMode: isSwitched ? SelectionMode.MULTI : SelectionMode.SINGLE,
        weekdayLabelsRow: NewCustomWeekdayLabelsRow(),
        onTap: (date) {});

    return Scaffold(
      backgroundColor: bgColor,
      appBar: AppBar(
        leading: IconButton(
            icon: Icon(
              Icons.arrow_back,
              color: Colors.black,
            ),
            onPressed: () {
              curDay = DateTime.now().day;
              for (int i = 0; i < mCalender.length; i++) {
                mCalender[i].bre = oldCalender[i].bre;
                mCalender[i].lun = oldCalender[i].lun;
                mCalender[i].sna = oldCalender[i].sna;
                mCalender[i].din = oldCalender[i].din;
                mCalender[i].ebre = oldCalender[i].ebre;
                mCalender[i].elun = oldCalender[i].elun;
                mCalender[i].esna = oldCalender[i].esna;
                mCalender[i].edin = oldCalender[i].edin;
              }
              for (int i = 0; i < nextmCalender.length; i++) {
                nextmCalender[i].bre = nextoldCalender[i].bre;
                nextmCalender[i].lun = nextoldCalender[i].lun;
                nextmCalender[i].sna = nextoldCalender[i].sna;
                nextmCalender[i].din = nextoldCalender[i].din;
                nextmCalender[i].ebre = nextoldCalender[i].ebre;
                nextmCalender[i].elun = nextoldCalender[i].elun;
                nextmCalender[i].esna = nextoldCalender[i].esna;
                nextmCalender[i].edin = nextoldCalender[i].edin;
              }
              setState(() {
                nextMonth = false;
              });
              Navigator.pop(
                  context,
                  PageTransition(
                      type: PageTransitionType.rightToLeft, child: HomePage()));
            }),
        centerTitle: true,
        elevation: 0,
        backgroundColor: white,
        title: Text('Set Schedule', style: h3, textAlign: TextAlign.center),
      ),
      body: Column(
        children: <Widget>[
          Container(
            margin: EdgeInsets.only(top: 10, bottom: 10),
            height: 30.0,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: <Widget>[
                nextMonth
                    ? GestureDetector(
                        onTap: () {
                          setState(() {
                            multiDates.clear();
                            curDay = DateTime.now().day;
                            nextMonth = false;
                            print(nextMonth);
                          });
                        },
                        child: Container(
                          child: Icon(
                            Icons.navigate_before,
                          ),
                        ),
                      )
                    : SizedBox(),
                Text(
                  nextMonth
                      ? '${months[DateTime.now().month]}'
                      : '${months[DateTime.now().month - 1]}',
                  style: h5,
                ),
                newMonth && !nextMonth
                    ? GestureDetector(
                        onTap: () {
                          setState(() {
                            multiDates.clear();
                            curDay = 1;
                            nextMonth = true;
                            print(nextMonth);
                          });
                        },
                        child: Container(
                          child: Icon(
                            Icons.navigate_next,
                          ),
                        ),
                      )
                    : SizedBox(),
                SizedBox(
                  width: 20,
                ),
                Text(
                  'Set Multiple',
                  style: h7,
                ),
                Switch(
                  value: isSwitched,
                  onChanged: (value) {
                    setState(() {
                      isSwitched = value;
                      if (isSwitched) {
                        monthCalendarro.selectedDates = [];
                        multiDates.clear();
                        curDay = DateTime.now().add(new Duration(days: 2)).day;
                        bfButton = false;
                        lunButton = false;
                        snackButton = false;
                        dinnerButton = false;
                      } else {
                        curDay = DateTime.now().day;
                        bfButton = mCalender[curDay].bre;
                        lunButton = mCalender[curDay].lun;
                        snackButton = mCalender[curDay].sna;
                        dinnerButton = mCalender[curDay].din;
                      }
                    });
                  },
                  activeTrackColor: primaryColor,
                  activeColor: highlightColor,
                ),
              ],
            ),
          ),
          Container(
              height: 280,
              child: nextMonth ? nextMonthCalendarro : monthCalendarro),
          Column(
            children: [
              Row(
                children: [
                  Expanded(
                    child: Container(
                      width: 200,
                      margin: EdgeInsets.only(
                          left: 10, top: 5, bottom: 5, right: 10),
                      child: RaisedButton(
                        // padding:
                        //     EdgeInsets.only(left: 50, right: 48, top: 10, bottom: 10),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(24.0),
                        ),
                        color: nextMonth
                            ? (nextmCalender[curDay].ebre == false
                                ? Colors.grey
                                : bfButton
                                    ? primaryColor
                                    : Colors.white)
                            : (mCalender[curDay].ebre == false
                                ? Colors.grey
                                : bfButton
                                    ? primaryColor
                                    : Colors.white),
                        child: (Text('Breakfast', style: h7)),
                        onPressed: () {
                          setState(() {
                            print(curDay);
                            print(nextMonth);
                            if (!nextMonth) {
                              if (mCalender[curDay].ebre) {
                                bfButton = !bfButton;
                                if (isSwitched) {
                                  multiDates.forEach((i) {
                                    if (bfButton) {
                                      mCalender[i].bre = true;
                                    } else {
                                      mCalender[i].bre = false;
                                    }
                                  });
                                } else {
                                  if (bfButton) {
                                    mCalender[curDay].bre = true;
                                  } else {
                                    mCalender[curDay].bre = false;
                                  }
                                }

                                callback();
                              } else {
                                EasyLoading.showToast('Cannot be changed');
                              }
                            } else {
                              print("bol " +
                                  nextmCalender[curDay].ebre.toString());
                              if (nextmCalender[curDay].ebre) {
                                bfButton = !bfButton;
                                if (isSwitched) {
                                  multiDates.forEach((i) {
                                    if (bfButton) {
                                      nextmCalender[i].bre = true;
                                    } else {
                                      nextmCalender[i].bre = false;
                                    }
                                  });
                                } else {
                                  if (bfButton) {
                                    nextmCalender[curDay].bre = true;
                                  } else {
                                    nextmCalender[curDay].bre = false;
                                  }
                                }

                                callback();
                              } else {
                                EasyLoading.showToast('Cannot be changed');
                              }
                            }
                          });
                        },
                      ),
                    ),
                  ),
                  Expanded(
                    child: Container(
                      width: 200,
                      margin: EdgeInsets.only(
                          left: 10, top: 5, bottom: 5, right: 10),
                      child: RaisedButton(
                        // padding:
                        //     EdgeInsets.only(left: 50, right: 80, top: 10, bottom: 10),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(24.0),
                        ),
                        color: nextMonth
                            ? (nextmCalender[curDay].elun == false
                                ? Colors.grey
                                : lunButton
                                    ? primaryColor
                                    : Colors.white)
                            : (mCalender[curDay].elun == false
                                ? Colors.grey
                                : lunButton
                                    ? primaryColor
                                    : Colors.white),
                        child: (Text('Lunch', style: h7)),
                        onPressed: () {
                          setState(() {
                            if (!nextMonth) {
                              if (mCalender[curDay].elun) {
                                lunButton = !lunButton;
                                if (isSwitched) {
                                  multiDates.forEach((i) {
                                    mCalender[i].lun = lunButton;
                                  });
                                } else {
                                  if (lunButton) {
                                    mCalender[curDay].lun = true;
                                  } else {
                                    mCalender[curDay].lun = false;
                                  }
                                }

                                callback();
                              } else {
                                EasyLoading.showToast('Cannot be changed');
                              }
                            } else {
                              if (nextmCalender[curDay].elun) {
                                lunButton = !lunButton;
                                if (isSwitched) {
                                  multiDates.forEach((i) {
                                    nextmCalender[i].lun = lunButton;
                                  });
                                } else {
                                  if (lunButton) {
                                    nextmCalender[curDay].lun = true;
                                  } else {
                                    nextmCalender[curDay].lun = false;
                                  }
                                }

                                callback();
                              } else {
                                EasyLoading.showToast('Cannot be changed');
                              }
                            }
                          });
                        },
                      ),
                    ),
                  ),
                ],
              ),
              Row(children: [
                Expanded(
                  child: Container(
                    width: 200,
                    margin:
                        EdgeInsets.only(left: 10, top: 5, bottom: 5, right: 10),
                    child: RaisedButton(
                      // padding:
                      //     EdgeInsets.only(left: 50, right: 70, top: 10, bottom: 10),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(24.0),
                      ),
                      color: nextMonth
                          ? (nextmCalender[curDay].esna == false
                              ? Colors.grey
                              : snackButton
                                  ? primaryColor
                                  : Colors.white)
                          : (mCalender[curDay].esna == false
                              ? Colors.grey
                              : snackButton
                                  ? primaryColor
                                  : Colors.white),
                      child: (Text('Snacks', style: h7)),
                      onPressed: () {
                        setState(() {
                          if (!nextMonth) {
                            if (mCalender[curDay].esna) {
                              snackButton = !snackButton;
                              if (isSwitched) {
                                multiDates.forEach((i) {
                                  mCalender[i].sna = snackButton;
                                });
                              } else {
                                if (snackButton) {
                                  mCalender[curDay].sna = true;
                                } else {
                                  mCalender[curDay].sna = false;
                                }
                              }

                              callback();
                            } else {
                              EasyLoading.showToast('Cannot be changed');
                            }
                          } else {
                            if (nextmCalender[curDay].esna) {
                              snackButton = !snackButton;
                              if (isSwitched) {
                                multiDates.forEach((i) {
                                  nextmCalender[i].sna = snackButton;
                                });
                              } else {
                                if (snackButton) {
                                  nextmCalender[curDay].sna = true;
                                } else {
                                  nextmCalender[curDay].sna = false;
                                }
                              }
                              print(nextmCalender[curDay].sna);
                              print(nextoldCalender[curDay].sna);

                              callback();
                            } else {
                              EasyLoading.showToast('Cannot be changed');
                            }
                          }
                        });
                      },
                    ),
                  ),
                ),
                Expanded(
                  child: Container(
                    width: 200,
                    margin:
                        EdgeInsets.only(left: 10, top: 5, bottom: 5, right: 10),
                    child: RaisedButton(
                      // padding:
                      //     EdgeInsets.only(left: 50, right: 78, top: 10, bottom: 10),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(24.0),
                      ),
                      color: nextMonth
                          ? (nextmCalender[curDay].edin == false
                              ? Colors.grey
                              : dinnerButton
                                  ? primaryColor
                                  : Colors.white)
                          : (mCalender[curDay].edin == false
                              ? Colors.grey
                              : dinnerButton
                                  ? primaryColor
                                  : Colors.white),
                      child: (Text('Dinner', style: h7)),
                      onPressed: () {
                        setState(() {
                          if (!nextMonth) {
                            if (mCalender[curDay].edin) {
                              dinnerButton = !dinnerButton;
                              if (isSwitched) {
                                multiDates.forEach((i) {
                                  print(i);
                                  mCalender[i].din = dinnerButton;
                                });
                              } else {
                                if (dinnerButton) {
                                  mCalender[curDay].din = true;
                                } else {
                                  mCalender[curDay].din = false;
                                }
                              }

                              callback();
                            } else {
                              EasyLoading.showToast('Cannot be changed');
                            }
                          } else {
                            if (nextmCalender[curDay].edin) {
                              dinnerButton = !dinnerButton;
                              if (isSwitched) {
                                multiDates.forEach((i) {
                                  print(i);
                                  nextmCalender[i].din = dinnerButton;
                                });
                              } else {
                                if (dinnerButton) {
                                  nextmCalender[curDay].din = true;
                                } else {
                                  nextmCalender[curDay].din = false;
                                }
                              }

                              callback();
                            } else {
                              EasyLoading.showToast('Cannot be changed');
                            }
                          }
                        });
                      },
                    ),
                  ),
                ),
              ]),
            ],
          ),
          Spacer(),
          FlatButton(
            child: Container(
              margin: EdgeInsets.all(5),

              decoration: BoxDecoration(
                color: Colors.greenAccent,
                borderRadius: BorderRadius.all(Radius.circular(10.0)),
              ),
              height: 60,
              alignment: Alignment.center,
              // margin: EdgeInsets.only(top: 80),
              padding: EdgeInsets.all(5),
              width: double.infinity,
              child: Center(
                child: Text(
                  "Save",
                  style: h8,
                ),
              ),
            ),
            onPressed: () {
              curDay = DateTime.now().day;
              Loader.show(
                context,
                progressIndicator: CircularProgressIndicator(
                  backgroundColor: Colors.white,
                ),
              );

              updateCalendar().then((value) {
                for (int i = 0; i < mCalender.length; i++) {
                  oldCalender[i].bre = mCalender[i].bre;
                  oldCalender[i].lun = mCalender[i].lun;
                  oldCalender[i].sna = mCalender[i].sna;
                  oldCalender[i].din = mCalender[i].din;
                  oldCalender[i].ebre = mCalender[i].ebre;
                  oldCalender[i].elun = mCalender[i].elun;
                  oldCalender[i].esna = mCalender[i].esna;
                  oldCalender[i].edin = mCalender[i].edin;
                }
                for (int i = 0; i < nextmCalender.length; i++) {
                  nextoldCalender[i].bre = nextmCalender[i].bre;
                  nextoldCalender[i].lun = nextmCalender[i].lun;
                  nextoldCalender[i].sna = nextmCalender[i].sna;
                  nextoldCalender[i].din = nextmCalender[i].din;
                  nextoldCalender[i].ebre = nextmCalender[i].ebre;
                  nextoldCalender[i].elun = nextmCalender[i].elun;
                  nextoldCalender[i].esna = nextmCalender[i].esna;
                  nextoldCalender[i].edin = nextmCalender[i].edin;
                }
                Loader.hide();
                selectedIndex = 2;
                setState(() {
                  nextMonth = false;
                });
                Navigator.pop(
                    context,
                    PageTransition(
                        type: PageTransitionType.rightToLeft,
                        child: HomePage()));
              });
            },
          ),
        ],
      ),
    );
  }
}

class NewCustomWeekdayLabelsRow extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Row(
      children: <Widget>[],
    );
  }
}

class CustomWeekdayLabelsRow extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Row(
      children: <Widget>[
        Expanded(child: Text("M", textAlign: TextAlign.center)),
        Expanded(child: Text("T", textAlign: TextAlign.center)),
        Expanded(child: Text("W", textAlign: TextAlign.center)),
        Expanded(child: Text("T", textAlign: TextAlign.center)),
        Expanded(child: Text("F", textAlign: TextAlign.center)),
        Expanded(child: Text("S", textAlign: TextAlign.center)),
        Expanded(child: Text("S", textAlign: TextAlign.center)),
      ],
    );
  }
}

class DaysViewTileBuilder extends DayTileBuilder {
  DateTime tileDate;
  CalendarroState calendarro;
  Function() callback;
  DaysViewTileBuilder(this.callback);

  @override
  Widget build(
      BuildContext context, DateTime tileDate, DateTimeCallback onTap) {
    calendarro = Calendarro.of(context);
    return new DateTileView(
      date: tileDate,
      calendarro: calendarro,
      callback: callback,
    );
  }
}

class DateTileView extends StatefulWidget {
  DateTime date;
  CalendarroState calendarro;
  Function() callback;

  DateTileView({this.date, this.calendarro, this.callback});

  @override
  State<DateTileView> createState() {
    return new DateTileState(date: date);
  }
}

class DateTileState extends State<DateTileView> {
  DateTime date;
  CalendarroState calendarro;
  StreamSubscription reservationsUpdatedEventSubscription;

  DateTileState({this.date, this.calendarro});

  @override
  @override
  void dispose() {
    //  reservationsUpdatedEventSubscription.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    var textColor = Colors.black;

    bool old =
        date.day < DateTime.now().day && date.month == DateTime.now().month;
    calendarro = Calendarro.of(context);
    bool isSelected = calendarro.isDateSelected(date);
    for (int i = 0; i < calendarro.selectedDates.length;) {
      if (!multiDates.contains(calendarro.selectedDates[i].day)) {
        calendarro.selectedDates.removeAt(i);
      } else {
        i++;
      }
    }
    print(calendarro.selectedDates);
    BoxDecoration boxDecoration;
    if (isSelected) {
      boxDecoration = new BoxDecoration(
          color: Colors.greenAccent.shade100, shape: BoxShape.circle);
    } else {
      boxDecoration = new BoxDecoration(
          border: new Border.all(
            color: Colors.white,
            width: 1.0,
          ),
          shape: BoxShape.circle);
    }

    var stackChildren = <Widget>[];
    if (nextMonth) {
      stackChildren = [
        Center(
            child: new Text(
          "${date.day}",
          textAlign: TextAlign.center,
          style: new TextStyle(color: textColor),
        )),
        Container(
          margin: EdgeInsets.all(1),
          height: 5,
          decoration: BoxDecoration(
            color: old
                ? Colors.grey
                : nextmCalender[date.day].bre
                    ? Colors.green.shade400
                    : Colors.black,
            shape: BoxShape.circle,
          ),
        ),
        Container(
          margin: EdgeInsets.all(1),
          height: 5,
          decoration: BoxDecoration(
            color: old
                ? Colors.grey
                : nextmCalender[date.day].lun
                    ? Colors.green.shade400
                    : Colors.black,
            shape: BoxShape.circle,
          ),
        ),
        Container(
          margin: EdgeInsets.all(1),
          height: 5,
          decoration: BoxDecoration(
            color: old
                ? Colors.grey
                : nextmCalender[date.day].sna
                    ? Colors.green.shade400
                    : Colors.black,
            shape: BoxShape.circle,
          ),
        ),
        Container(
          margin: EdgeInsets.all(1),
          height: 5,
          decoration: BoxDecoration(
            color: old
                ? Colors.grey
                : nextmCalender[date.day].din
                    ? Colors.green.shade400
                    : Colors.black,
            shape: BoxShape.circle,
          ),
        ),
      ];
    } else {
      stackChildren = [
        Center(
            child: new Text(
          "${date.day}",
          textAlign: TextAlign.center,
          style: new TextStyle(color: textColor),
        )),
        Container(
          margin: EdgeInsets.all(1),
          height: 5,
          decoration: BoxDecoration(
            color: old
                ? Colors.grey
                : mCalender[date.day].bre
                    ? Colors.green.shade400
                    : Colors.black,
            shape: BoxShape.circle,
          ),
        ),
        Container(
          margin: EdgeInsets.all(1),
          height: 5,
          decoration: BoxDecoration(
            color: old
                ? Colors.grey
                : mCalender[date.day].lun
                    ? Colors.green.shade400
                    : Colors.black,
            shape: BoxShape.circle,
          ),
        ),
        Container(
          margin: EdgeInsets.all(1),
          height: 5,
          decoration: BoxDecoration(
            color: old
                ? Colors.grey
                : mCalender[date.day].sna
                    ? Colors.green.shade400
                    : Colors.black,
            shape: BoxShape.circle,
          ),
        ),
        Container(
          margin: EdgeInsets.all(1),
          height: 5,
          decoration: BoxDecoration(
            color: old
                ? Colors.grey
                : mCalender[date.day].din
                    ? Colors.green.shade400
                    : Colors.black,
            shape: BoxShape.circle,
          ),
        ),
      ];
    }

    return new Expanded(
        child: new GestureDetector(
      behavior: HitTestBehavior.translucent,
      child: new Container(
          height: 50,
          width: 40,
          decoration: boxDecoration,
          child: Column(children: stackChildren)),
      onTap: handleTap,
    ));
  }

  void handleTap() {
    if (date.day < DateTime.now().day && date.month == DateTime.now().month) {
      return;
    }
    if (isSwitched && date.difference(DateTime.now()).inHours < 13) {
      EasyLoading.showToast('This date cannot be used for multiple selection');
      return;
    }
    calendarro.setSelectedDate(date);
    calendarro.setCurrentDate(date);

    if (isSwitched) {
      if (calendarro.isDateSelected(date))
        multiDates.add(date.day);
      else {
        multiDates.remove(date.day);
      }
    }
    if (!nextMonth) {
      if (isSwitched &&
          multiDates.isNotEmpty &&
          calendarro.isDateSelected(date)) {
        if (mCalender[multiDates.first].bre) {
          mCalender[date.day].bre = true;
        } else {
          mCalender[date.day].bre = false;
        }
        if (mCalender[multiDates.first].lun) {
          mCalender[date.day].lun = true;
        } else {
          mCalender[date.day].lun = false;
        }
        if (mCalender[multiDates.first].sna) {
          mCalender[date.day].sna = true;
        } else {
          mCalender[date.day].sna = false;
        }
        if (mCalender[multiDates.first].din) {
          mCalender[date.day].din = true;
        } else {
          mCalender[date.day].din = false;
        }
      }
      bfButton = mCalender[date.day].bre;
      lunButton = mCalender[date.day].lun;
      snackButton = mCalender[date.day].sna;
      dinnerButton = mCalender[date.day].din;
    } else {
      if (isSwitched &&
          multiDates.isNotEmpty &&
          calendarro.isDateSelected(date)) {
        if (nextmCalender[multiDates.first].bre) {
          nextmCalender[date.day].bre = true;
        } else {
          nextmCalender[date.day].bre = false;
        }
        if (nextmCalender[multiDates.first].lun) {
          nextmCalender[date.day].lun = true;
        } else {
          nextmCalender[date.day].lun = false;
        }
        if (nextmCalender[multiDates.first].sna) {
          nextmCalender[date.day].sna = true;
        } else {
          nextmCalender[date.day].sna = false;
        }
        if (nextmCalender[multiDates.first].din) {
          nextmCalender[date.day].din = true;
        } else {
          nextmCalender[date.day].din = false;
        }
      }
      bfButton = nextmCalender[date.day].bre;
      lunButton = nextmCalender[date.day].lun;
      snackButton = nextmCalender[date.day].sna;
      dinnerButton = nextmCalender[date.day].din;
    }

    if (!isSwitched) {
      curDay = calendarro.selectedSingleDate.day;
    }
    print("cur" + curDay.toString());
    widget.callback();
  }
}
