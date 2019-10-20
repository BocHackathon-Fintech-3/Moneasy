package com.example.eaze;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.drawable.Animatable2;
import android.graphics.drawable.AnimatedVectorDrawable;
import android.graphics.drawable.Drawable;
import android.os.Bundle;
import android.os.Handler;
import android.util.Log;
import android.view.View;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.TextView;

import com.google.android.material.floatingactionbutton.FloatingActionButton;

public class MainActivity extends AppCompatActivity {
    public static final String PREFS_NAME= "CREDENTIALS";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        final TextView writer = findViewById(R.id.text);
        final EditText email = findViewById(R.id.email);

        FloatingActionButton fab = findViewById(R.id.register);
        final String text = "Is this your email address?";
        for(int i=0;i<text.length();i++){
            final int j = i;
            final Handler handler = new Handler();
            handler.postDelayed(new Runnable() {
                @Override
                public void run() {
                    Log.e("nah", String.valueOf(text.charAt(j)));
                    writer.setText(writer.getText().toString() + text.charAt(j));
                }
            }, i*100);
        }
        fab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Log.e("asl", "push");
                SharedPreferences.Editor editor = getSharedPreferences(PREFS_NAME, MODE_PRIVATE).edit();
                editor.putString("email", email.getText().toString());
                editor.apply();
                Log.e("asl", "push2");

                Intent intent = new Intent(MainActivity.this, UploadPicsActivity.class);
                startActivity(intent);

            }
        });
    }
}
