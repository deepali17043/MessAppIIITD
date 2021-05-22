import 'package:flutter/material.dart';
import 'package:flutter_easyloading/flutter_easyloading.dart';
import './src/screens/signin_page.dart';
import 'start_page.dart';
import 'package:loader_overlay/loader_overlay.dart';

void main() => runApp(MyApp());

class MyApp extends StatelessWidget {
  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return GlobalLoaderOverlay(
        useDefaultLoading: true,
        child: MaterialApp(
          title: 'Aahar',
          theme: ThemeData(
            primarySwatch: Colors.green,
          ),
          home: StartPage(pageTitle: 'Welcome'),
          routes: <String, WidgetBuilder>{
            '/signin': (BuildContext context) => SignInPage(),
          },
          builder: EasyLoading.init(),
        ));
  }
}
