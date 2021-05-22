import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';
import 'package:fryo/src/screens/signin_page.dart';
import '../screens/home_page.dart';
import '../screens/vendor_page.dart';

import '../shared/text_field_container.dart';
import '../shared/styles.dart';
import '../shared/colors.dart';
import 'package:page_transition/page_transition.dart';
import 'package:http/http.dart';
import 'dart:convert';
import '../shared/buttons.dart';
import '../shared/creds.dart';
import 'package:flutter_easyloading/flutter_easyloading.dart';

class SignUpPage extends StatefulWidget {
  final String pageTitle;

  SignUpPage({Key key, this.pageTitle}) : super(key: key);

  @override
  _SignUpPageState createState() => _SignUpPageState();
}

class _SignUpPageState extends State<SignUpPage> {
  final usernameController = TextEditingController();
  final emailController = TextEditingController();
  final passController = TextEditingController();
  final cpassController = TextEditingController();

  Future<Map> register(String username, String name, String email, String type,
      String password) async {
    Response response = await post(
      url + 'api/signup/',
      headers: <String, String>{
        'Content-Type': 'application/json; charset=UTF-8',
      },
      body: jsonEncode(<String, String>{
        'username': username,
        'name': name,
        'email': email,
        'type': type,
        'password': password,
        'validate_password': password,
      }),
    );
    var decode = jsonDecode(response.body);
    print(decode);
    return decode;
  }

  @override
  Widget build(BuildContext context) {
    Size size = MediaQuery.of(context).size;
    return Scaffold(
      appBar: AppBar(
        elevation: 0,
        backgroundColor: white,
        title: Center(
          child: Text('Sign Up', style: h3),
        ),
        actions: <Widget>[],
        leading: IconButton(
          icon: Icon(Icons.arrow_back),
          color: Colors.black,
          onPressed: () {
            Navigator.pop(context);
          },
        ),
      ),
      body: ListView(
        children: <Widget>[
          Container(
            padding: EdgeInsets.only(top: 10, left: 18, right: 18),
            child: Stack(
              children: <Widget>[
                Padding(
                  padding: const EdgeInsets.all(20.0),
                  child: Container(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.start,
                      crossAxisAlignment: CrossAxisAlignment.center,
                      children: <Widget>[
                        Container(
                          child: Text('Create your Aahar Account',
                              style: logoStyle2),
                        ),
                        SizedBox(
                          height: size.height * 0.05,
                        ),
                        TextFieldContainer(
                          child: TextField(
                              controller: usernameController,
                              decoration: InputDecoration(
                                hintText: "Username",
                              )),
                        ),
                        TextFieldContainer(
                          child: TextField(
                              controller: emailController,
                              decoration: InputDecoration(
                                hintText: "Email",
                              )),
                        ),
                        TextFieldContainer(
                          child: TextField(
                              obscureText: true,
                              controller: passController,
                              decoration: InputDecoration(
                                hintText: "Password",
                              )),
                        ),
                        TextFieldContainer(
                          child: TextField(
                              obscureText: true,
                              controller: cpassController,
                              decoration: InputDecoration(
                                hintText: "Confirm Password",
                              )),
                        ),
                        mFlatBtn(
                            text: 'Sign Up',
                            onPressed: () {
                              if (cpassController.text == passController.text) {
                                register(
                                        usernameController.text,
                                        usernameController.text,
                                        emailController.text,
                                        'customer',
                                        passController.text)
                                    .then((value) {
                                  if (value['response'] ==
                                      "successful registration") {
                                    EasyLoading.showToast('SignUp Successful');
                                    Navigator.pushReplacement(
                                        context,
                                        PageTransition(
                                            type:
                                                PageTransitionType.rightToLeft,
                                            child: SignInPage()));
                                  } else if (value.containsKey('response') ==
                                      false) {
                                    EasyLoading.showToast(value.toString());
                                  }
                                  //

                                  // if (value == "successful registration") {
                                  //
                                  //   Navigator.pushReplacement(
                                  //       context,
                                  //       PageTransition(
                                  //           type:
                                  //               PageTransitionType.rightToLeft,
                                  //           child: HomePage()));
                                  // }
                                });
                              } else {}
                            }),
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
    );
  }
}
