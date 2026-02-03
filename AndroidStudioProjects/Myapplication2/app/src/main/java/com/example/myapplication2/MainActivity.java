package com.example.myapplication2;

import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;

// PROJECT 1: Calculator app in Java
// NOTE: works for one operation at a time

// MainActivity -> screen, AppCompatActivity -> gives u access to views resources and themes
public class MainActivity extends AppCompatActivity {
    // -------- UI references (attributes)----------
    private EditText editText;
    private TextView resultText;
    private Button addButton, subtractButton, multiplyButton, divideButton, equalButton, clearButton;
    private Button num1Button, num2Button, num3Button, num4Button;
    private Button num5Button, num6Button, num7Button, num8Button, num9Button, zeroButton, dotButton;
    //-----------------------------
    // ------- Calculator variables ----------
    private double num1, num2;
    private boolean isAddition, isSubtraction, isMultiplication, isDivision;
    // ---------------------------

    @Override // <-- kinda like virtual function
    // App startup
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        // loads XML Layout aka UI
        setContentView(R.layout.activity_main);

        // get ID from XML, stores in java variable
        editText = findViewById(R.id.editText2);
        resultText = findViewById(R.id.resultText);
        clearButton = findViewById(R.id.clear_text);

        addButton = findViewById(R.id.add);
        subtractButton = findViewById(R.id.sub);
        multiplyButton = findViewById(R.id.mul);
        divideButton = findViewById(R.id.div);
        equalButton = findViewById(R.id.submit);

        num1Button = findViewById(R.id.num1);
        num2Button = findViewById(R.id.num2);
        num3Button = findViewById(R.id.num3);
        num4Button = findViewById(R.id.num4);
        num5Button = findViewById(R.id.num5);
        num6Button = findViewById(R.id.num6);
        num7Button = findViewById(R.id.num7);
        num8Button = findViewById(R.id.num8);
        num9Button = findViewById(R.id.num9);
        zeroButton = findViewById(R.id.zero);
        dotButton = findViewById(R.id.dot);

        // --- button functionality ----
        addButton.setOnClickListener(new View.OnClickListener() {
            @Override
            // when button clicked
            public void onClick(View v) {
                // if the input has at least one digit
                if (editText.getText().length() > 0) {
                    // convert string to number
                    num1 = Double.parseDouble(editText.getText().toString());
                    // set addition flag to true
                    isAddition = true;

                    // Clear the EditText for the next number
                    editText.setText("");
                }
            }
        });

        subtractButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (editText.getText().length() > 0) {
                    num1 = Double.parseDouble(editText.getText().toString());
                    isSubtraction = true;

                    // Clear the EditText for the next number
                    editText.setText("");
                }
            }
        });

        multiplyButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (editText.getText().length() > 0) {
                    num1 = Double.parseDouble(editText.getText().toString());
                    isMultiplication = true;

                    // Clear the EditText for the next number
                    editText.setText("");
                }
            }
        });

        divideButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (editText.getText().length() > 0) {
                    num1 = Double.parseDouble(editText.getText().toString());
                    isDivision = true;

                    // Clear the EditText for the next number
                    editText.setText("");
                }
            }
        });

        clearButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                editText.setText("");
                resultText.setText("0");
                // Reset all flags
                isAddition = false;
                isSubtraction = false;
                isMultiplication = false;
                isDivision = false;
            }
        });

        equalButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (editText.getText().length() > 0) {
                    num2 = Double.parseDouble(editText.getText().toString());
                    if (isAddition) {
                        resultText.setText(String.valueOf(num1 + num2));
                    } else if (isSubtraction) {
                        resultText.setText(String.valueOf(num1 - num2));
                    } else if (isMultiplication) {
                        resultText.setText(String.valueOf(num1 * num2));
                    } else if (isDivision) {
                        if (num2 != 0) {
                            resultText.setText(String.valueOf(num1 / num2));
                        } else {
                            resultText.setText("Error");
                        }
                    }
                    // Reset all flags
                    isAddition = false;
                    isSubtraction = false;
                    isMultiplication = false;
                    isDivision = false;
                }
            }
        });

        num1Button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                editText.setText(editText.getText().toString() + "1");
            }
        });

        num2Button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                editText.setText(editText.getText().toString() + "2");
            }
        });

        num3Button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                editText.setText(editText.getText().toString() + "3");
            }
        });

        num4Button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                editText.setText(editText.getText().toString() + "4");
            }
        });

        num5Button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                editText.setText(editText.getText().toString() + "5");
            }
        });

        num6Button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                editText.setText(editText.getText().toString() + "6");
            }
        });

        num7Button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                editText.setText(editText.getText().toString() + "7");
            }
        });

        num8Button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                editText.setText(editText.getText().toString() + "8");
            }
        });

        num9Button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                editText.setText(editText.getText().toString() + "9");
            }
        });

        zeroButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                editText.setText(editText.getText().toString() + "0");
            }
        });

        dotButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (!editText.getText().toString().contains(".")) {
                    editText.setText(editText.getText().toString() + ".");
                }
            }
        });
        // -------------
    }
}