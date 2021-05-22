import 'package:flutter/material.dart';
import 'package:flutter_overlay_loader/flutter_overlay_loader.dart';
import 'package:fryo/src/shared/creds.dart';
import 'package:loader_overlay/loader_overlay.dart';
import 'src/screens/home_page.dart';
import 'src/shared/styles.dart';
import 'src/shared/colors.dart';
import 'src/shared/buttons.dart';
import 'package:page_transition/page_transition.dart';
import 'src/screens/signin_page.dart';
import 'src/screens/signup_page.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';

bool isLoggedIn = false;
String name = '';
String password = '';

class StartPage extends StatefulWidget {
  final String pageTitle;

  StartPage({Key key, this.pageTitle}) : super(key: key);

  @override
  _StartPageState createState() => _StartPageState();
}

class _StartPageState extends State<StartPage> {
  @override
  void initState() {
    super.initState();
    autoLogIn();
  }

  @mustCallSuper
  @protected
  void dispose() {
    // TODO: implement dispose
    //  WidgetsBinding.instance.removeObserver(this);

    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return LoaderOverlay(
        overlayWidget: Center(
          child: SpinKitCubeGrid(
            color: Colors.red,
            size: 50.0,
          ),
        ),
        overlayOpacity: 0.8,
        child: Scaffold(
          body: Center(
              child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: <Widget>[
              Image.asset('images/welcome.jpg', width: 190, height: 120),
              Container(
                margin: EdgeInsets.only(bottom: 40, top: 0),
                child: Text('Aahar', style: logoStyle),
              ),
              Container(
                width: 200,
                margin: EdgeInsets.only(bottom: 0),
                child: mFlatBtn(
                    text: 'Sign In',
                    onPressed: () {
                      Navigator.pushReplacement(
                          context,
                          PageTransition(
                              type: PageTransitionType.rightToLeft,
                              duration: Duration(seconds: 1),
                              child: SignInPage()));
                    }),
              ),
              Container(
                width: 200,
                padding: EdgeInsets.all(0),
                child: mOutlineBtn('Sign Up', () {
                  Navigator.push(
                      context,
                      PageTransition(
                          type: PageTransitionType.rightToLeft,
                          child: SignUpPage()));
                }),
              ),
            ],
          )),
          backgroundColor: bgColor,
        ));
  }

  void autoLogIn() async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    final String userId = prefs.getString('username');
    final String passId = prefs.getString('password');

    if (userId != null) {
      Loader.show(
        context,
        progressIndicator: CircularProgressIndicator(
          backgroundColor: Colors.white,
        ),
      );
      login(userId, passId).then((value) {
        setState(() {
          if (value) {
            isLoggedIn = true;
            name = userId;
            password = passId;
            Loader.hide();
            Navigator.pushReplacement(
                context,
                PageTransition(
                    type: PageTransitionType.rightToLeft, child: HomePage()));
          } else {
            Loader.hide();
          }
        });
      });

      return;
    }
  }
}
