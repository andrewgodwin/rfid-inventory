package org.aeracode.inventory.clients.androidclient;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.TextView;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

import com.zebra.rfid.api3.TagData;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

public class MainActivity extends AppCompatActivity implements RFIDHandler.ResponseHandlerInterface {

    public TextView readerStatus = null;
    private TextView textrfid;
    private TextView testStatus;
    private TextView tagStatus;

    RFIDHandler rfidHandler;
    private Set<String> seenTags = new HashSet<String>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        // UI
        readerStatus = findViewById(R.id.readerStatus);
        tagStatus = findViewById(R.id.tagStatus);
        textrfid = findViewById(R.id.textViewdata);
        testStatus = findViewById(R.id.testStatus);

        // RFID Handler
        rfidHandler = new RFIDHandler();
        rfidHandler.onCreate(this);

        // Settings
        android.support.v7.preference.PreferenceManager
                .setDefaultValues(this, R.xml.preferences, false);
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        if (id == R.id.action_settings) {
            Intent intent = new Intent(this, SettingsActivity.class);
            startActivity(intent);
            return true;
        }

        return super.onOptionsItemSelected(item);
    }

    @Override
    protected void onPause() {
        super.onPause();
        rfidHandler.onPause();
    }

    @Override
    protected void onPostResume() {
        super.onPostResume();
        String status = rfidHandler.onResume();
        readerStatus.setText(status);
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        rfidHandler.onDestroy();
    }


    @Override
    public void handleTagdata(TagData[] tagData) {
        // Show on screen
        final StringBuilder sb = new StringBuilder();
        for (int index = 0; index < tagData.length; index++) {
            sb.append(tagData[index].getTagID() + "\n");
            seenTags.add("epc:" + tagData[index].getTagID());
        }
        final String tagsText = seenTags.size() + " tags";

        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                textrfid.setText(sb.toString());
                tagStatus.setText(tagsText);
            }
        });
    }

    public void scanFinished() {
        // Get token
        SharedPreferences sharedPref =
                android.support.v7.preference.PreferenceManager
                        .getDefaultSharedPreferences(this);
        String token = sharedPref.getString("token", "");
        if (token.length() < 1) {
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    textrfid.setText("No token set");
                }
            });
            return;
        }
        // Create JSON body
        JSONObject postBody = new JSONObject();
        try {
            postBody.put("token", token);
            postBody.put("tags", new JSONArray(seenTags));
        } catch (final JSONException e) {
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    textrfid.setText("JSON error: " + e);
                }
            });
            return;
        }
        // Send to server
        JSONObject tagNames;
        try {
            URL url = new URL(sharedPref.getString("apiUrl", "https://inventory.aeracode.org/api/device/sync/"));
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("POST");
            conn.setRequestProperty("Content-Type", "application/json;charset=UTF-8");
            conn.setRequestProperty("Accept","application/json");
            conn.setDoOutput(true);
            conn.setDoInput(true);
            try(OutputStream os = conn.getOutputStream()){
                byte[] input = postBody.toString().getBytes("utf-8");
                os.write(input, 0, input.length);
            }
            Log.i("STATUS", String.valueOf(conn.getResponseCode()));
            // Read response
            BufferedReader br = new BufferedReader(new InputStreamReader(conn.getInputStream()));
            StringBuilder rsb = new StringBuilder();
            String line;
            while ((line = br.readLine()) != null) {
                rsb.append(line + "\n");
            }
            br.close();
            conn.disconnect();
            JSONObject responseJson = new JSONObject(rsb.toString());
            tagNames = responseJson.getJSONObject("tag_names");

            // Show number of tags
            final String tagsText = seenTags.size() + " tags";
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    tagStatus.setText(tagsText);
                }
            });

            // Show tag list
            final StringBuilder sb = new StringBuilder();
            for (String tag : seenTags) {
                if (tagNames != null && tagNames.has(tag)) {
                    sb.append(tagNames.getString(tag) + " (" + tag + ")\n");
                } else {
                    sb.append(tag + "\n");
                }
            }
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    textrfid.setText(sb.toString());
                }
            });
        } catch (final IOException e) {
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    textrfid.setText("URL error: " + e);
                }
            });
            return;
        } catch (final JSONException e) {
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    textrfid.setText("Response parse error: " + e);
                }
            });
            return;
        }

        // Wipe set
        seenTags.clear();
    }

    @Override
    public void handleTriggerPress(boolean pressed) {
        if (pressed) {
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    textrfid.setText("");
                }
            });
            rfidHandler.performInventory();
        } else {
            rfidHandler.stopInventory();
            scanFinished();
        }
    }
}
