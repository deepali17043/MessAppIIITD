import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';
import 'package:loader_overlay/loader_overlay.dart';
import '../../start_page.dart';
import '../screens/home_page.dart';
import '../screens/vendor_page.dart';
import '../screens/signup_page.dart';

import '../shared/text_field_container.dart';
import '../shared/styles.dart';
import '../shared/colors.dart';
import 'package:page_transition/page_transition.dart';
import 'package:http/http.dart';
import 'dart:convert';
import '../shared/buttons.dart';
import '../shared/creds.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';
import 'package:flutter_overlay_loader/flutter_overlay_loader.dart';

Future<bool> login(String uName, pass) async {
  SharedPreferences prefs = await SharedPreferences.getInstance();

  Response response = await post(
    url + 'api-token-auth/',
    headers: <String, String>{
      'Content-Type': 'application/json; charset=UTF-8',
    },
    body: jsonEncode(<String, String>{
      'username': uName,
      'password': pass,
    }),
  );
  print('hi');
  print(response.body);
  if (response.body.contains('token')) {
    userToken = 'Token ' + jsonDecode(response.body)['token'];
    prefs.setString('username', uName);
    prefs.setString('password', pass);
    return true;
  } else {
    return false;
  }
}

class SignInPage extends StatefulWidget {
  final String pageTitle;
  String wrongCred = '';

  SignInPage({Key key, this.pageTitle}) : super(key: key);

  @override
  _SignInPageState createState() => _SignInPageState();
}

class _SignInPageState extends State<SignInPage> {
  SharedPreferences prefs;

  void getVendorList() async {
    Response response = await get(
      'http://cf03fe8f0833.ngrok.io/api/user/dashboard/',
      headers: {
        'Authorization': "Token 57eff58c5cc493837b62b3b7f59ad19a6b633f4b",
        'username': 'user1',
        'password': 'user1pwd@123',
      },
    );

    print(response.body);
  }

  String emailController = '';
  String passController = '';

  @mustCallSuper
  @protected
  void dispose() {
    // TODO: implement dispose
    //  WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    //  getVendorList();
    //   login('user1', 'user1pwd@123');

    Size size = MediaQuery.of(context).size;
    return LoaderOverlay(
        overlayWidget: Center(
          child: SpinKitCubeGrid(
            color: Colors.red,
            size: 50.0,
          ),
        ),
        overlayOpacity: 0.8,
        child: Scaffold(
          appBar: AppBar(
            elevation: 0,
            backgroundColor: white,
            title: Center(
              child: Text('Sign In', style: h3),
            ),
            actions: <Widget>[],
          ),
          body: ListView(
            children: <Widget>[
              Container(
                padding: EdgeInsets.only(top: 100, left: 18, right: 18),
                child: Stack(
                  children: <Widget>[
                    Padding(
                      padding: const EdgeInsets.all(30.0),
                      child: Container(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.start,
                          crossAxisAlignment: CrossAxisAlignment.center,
                          children: <Widget>[
                            Container(
                              child: Text('Hi there', style: logoStyle),
                            ),
                            SizedBox(
                              height: size.height * 0.1,
                            ),
                            Text(
                              widget.wrongCred,
                              style: wrongText,
                            ),
                            TextFieldContainer(
                              child: TextField(
                                //          controller: emailController,
                                decoration: InputDecoration(
                                  hintText: "Your Username",
                                ),
                                onChanged: (value) {
                                  emailController = value;
                                },
                              ),
                            ),
                            TextFieldContainer(
                              child: TextField(
                                obscureText: true,
                                //  controller: passController,
                                decoration: InputDecoration(
                                  hintText: "Password",
                                ),
                                onChanged: (value) {
                                  passController = value;
                                },
                              ),
                            ),
                            mFlatBtn(
                                text: 'Sign In',
                                onPressed: () {
                                  Loader.show(
                                    context,
                                    progressIndicator:
                                        CircularProgressIndicator(
                                      backgroundColor: Colors.white,
                                    ),
                                  );
                                  login(emailController, passController)
                                      .then((value) {
                                    Loader.hide();
                                    setState(() {
                                      if (value) {
                                        Navigator.pushReplacement(
                                            context,
                                            PageTransition(
                                                type: PageTransitionType
                                                    .rightToLeft,
                                                child: HomePage()));
                                      } else {
                                        widget.wrongCred =
                                            'Incorrect Email or Password';
                                      }
                                    });
                                  });
                                }),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: <Widget>[
                                Text(
                                  "Don’t have an Account ? ",
                                  style: TextStyle(color: darkText),
                                ),
                                GestureDetector(
                                  onTap: () {
                                    Navigator.push(
                                        context,
                                        PageTransition(
                                            type:
                                                PageTransitionType.rightToLeft,
                                            child: SignUpPage()));
                                  },
                                  child: Text(
                                    "Sign Up",
                                    style: TextStyle(
                                      color: primaryColor,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                )
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
                height: size.height,
                width: double.infinity,
                color: bgColor,
              ),
            ],
          ),
        ));
  }
}
