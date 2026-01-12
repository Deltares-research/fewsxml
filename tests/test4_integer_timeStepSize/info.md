The multiplier value of the timeStepSize parameter must be an integer.
For example, the following line:

```XML
<timeStep unit="second" multiplier="600.0"/>
```
is incorrect because the multiplier is a floating-point number. It should be:

```XML
<timeStep unit="second" multiplier="600"/>
```