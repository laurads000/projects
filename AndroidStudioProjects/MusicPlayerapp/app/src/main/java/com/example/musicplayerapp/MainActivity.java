package com.example.musicplayerapp;

import android.media.MediaPlayer;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.View;
import android.widget.ImageView;
import android.widget.SeekBar;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;

import java.util.concurrent.TimeUnit;

public class MainActivity extends AppCompatActivity {

    // variables and UI elements
    private MediaPlayer mediaPlayer;
    // Declare UI elements
    private SeekBar progressBar;
    private TextView textCurrentTime;
    private TextView songData;
    private TextView songTime;
    private ImageView buttonPlay;
    private ImageView buttonPause;
    private ImageView buttonStop;

    // "Polling" mediaPlayer to update seekBar and time
    private final Handler songProgressHandler = new Handler(Looper.getMainLooper());

    // Runnable task that updates SeekBar and current playback time
    private final Runnable updateSeekBar = new Runnable() {
        public void run() {
            if (mediaPlayer != null && mediaPlayer.isPlaying()) {
                // Update SeekBar progress and current time text
                progressBar.setProgress(mediaPlayer.getCurrentPosition());
                textCurrentTime.setText(formatTime(mediaPlayer.getCurrentPosition()));

                // Repeat this task every 1 second
                songProgressHandler.postDelayed(this, 1000);
            }
        }
    };

    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // main layout
        setContentView(R.layout.activity_main);

        // initialize variables from UI (like view from mvvm)
        progressBar = findViewById(R.id.seekBar);               // <-- TODO: change later
        textCurrentTime = findViewById(R.id.textCurrentTime);
        songTime = findViewById(R.id.textTotalTime);            // <-- TODO: change later in .xml
        songData = findViewById(R.id.songData);
        buttonPlay = findViewById(R.id.buttonPlay);
        buttonPause = findViewById(R.id.buttonPause);
        buttonStop = findViewById(R.id.buttonStop);

        // Initially hide the pause button
        buttonPause.setVisibility(View.GONE);

        // instantiate mediaPlayer with sample1.mp3
        int mediaId = R.raw.specialz__king_gnu;
        mediaPlayer = MediaPlayer.create(this, mediaId);

        // sets up seek bar
        // waits for mediaPlayer to be ready, sets max of progressBar, and song time from mp3
        mediaPlayer.setOnPreparedListener(mp -> {
            progressBar.setMax(mp.getDuration());
            songTime.setText(formatTime(mp.getDuration()));

            // saving song title and artist

            String data = "";
            String fileName = getResources().getResourceEntryName(mediaId);
            int seperator = fileName.indexOf("__");
            if (seperator == -1) {
                data = fileName;
            } else {
                String title = fileName.substring(0, seperator);
                String artist = fileName.substring(seperator + 2);
                data = title + " (" + artist + ")";
                data = data.replace("_", " ");
                songData.setText(data);
            }

        });



        // play button starts song
        buttonPlay.setOnClickListener(v -> {
            mediaPlayer.start();
            songProgressHandler.post(updateSeekBar);
            buttonPlay.setVisibility(View.GONE);
            buttonPause.setVisibility(View.VISIBLE);
        });

        // pause button pauses song
        buttonPause.setOnClickListener(v -> {
            mediaPlayer.pause();
            buttonPause.setVisibility(View.GONE);
            buttonPlay.setVisibility(View.VISIBLE);
        });

        // stop button, like square restart button
        buttonStop.setOnClickListener(v -> {
            mediaPlayer.stop();
            mediaPlayer = MediaPlayer.create(this, R.raw.specialz__king_gnu);
            songTime.setText(formatTime(mediaPlayer.getDuration()));
            progressBar.setProgress(0);
            textCurrentTime.setText("0:00");
            buttonPause.setVisibility(View.GONE);
            buttonPlay.setVisibility(View.VISIBLE);

        });
        // For user interactions with seek bar, waiting if user changes seekBar
        progressBar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            // user used seek bar

            public void onProgressChanged(SeekBar progressBar, int progress, boolean fromUser) {
                if (fromUser && mediaPlayer != null) {
                    // Seek MediaPlayer to new position and update current time
                    mediaPlayer.seekTo(progress);
                    textCurrentTime.setText(formatTime(progress));
                }
            }

            // Not used, but required to override

            public void onStartTrackingTouch(SeekBar progressBar) {}

            // Not used, but required to override

            public void onStopTrackingTouch(SeekBar progressBar) {}
        });
    }

    // Format milliseconds into minutes:seconds format (e.g., 1:05)
    private String formatTime(int milliseconds) {
        long minutes = TimeUnit.MILLISECONDS.toMinutes(milliseconds);
        long seconds = TimeUnit.MILLISECONDS.toSeconds(milliseconds) % 60;
        return String.format("%d:%02d", minutes, seconds);
    }

    // Clean up MediaPlayer and handler when activity is destroyed
    public void onDestroy() {
        super.onDestroy();
        songProgressHandler.removeCallbacks(updateSeekBar);
        if (mediaPlayer != null) {
            mediaPlayer.release();
        }
    }
}