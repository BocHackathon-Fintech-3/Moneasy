package com.example.eaze;

import androidx.appcompat.app.AppCompatActivity;

import android.app.Application;
import android.content.ClipData;
import android.content.ContentValues;
import android.content.Intent;
import android.content.SharedPreferences;
import android.database.Cursor;
import android.net.Uri;
import android.os.Bundle;
import android.preference.PreferenceManager;
import android.provider.MediaStore;
import android.provider.SyncStateContract;
import android.util.Log;
import android.widget.Toast;

import com.boc.client.invoker.JSON;

import net.gotev.uploadservice.Logger;
import net.gotev.uploadservice.MultipartUploadRequest;
import net.gotev.uploadservice.UploadNotificationConfig;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.UUID;

import cdflynn.android.library.checkview.CheckView;
import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.FormBody;
import okhttp3.MultipartBody;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

import static com.example.eaze.Constants.*;
import static com.example.eaze.MainActivity.PREFS_NAME;

public class UploadPicsActivity extends AppCompatActivity {

    private static final int PICK_FROM_GALLERY = 2;
    private static final int ONEBANK_REQUEST = 702;
    private static final String URL = "http://192.168.10.140:5001";
    ArrayList<Uri> imagePaths = new ArrayList<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_upload_pics);
        Log.e("asl", "push2");
        if(getIntent().getData() != null && getIntent().getDataString() != null){
            Log.e("URL", getIntent().getDataString());
            mOath2 = getIntent().getDataString().substring(getIntent().getDataString().length() - 110);
            Log.e("oath", mOath2);
            secondAuthentication();
        }
        else{
            Intent galleryIntent = new Intent(Intent.ACTION_PICK, android.provider.MediaStore.Images.Media.EXTERNAL_CONTENT_URI);
            galleryIntent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, true);
            // Start the Intent
            startActivityForResult(galleryIntent, PICK_FROM_GALLERY);
        }


    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {

        String s = "";
        if (resultCode == RESULT_OK) {
            if (requestCode == PICK_FROM_GALLERY) {
                ClipData clipData = data.getClipData();


                if(clipData == null){
                    imagePaths.add(data.getData());
                }else{
                    s = "clipData != null\n";
                    for(int i=0; i<clipData.getItemCount(); i++){
                        ClipData.Item item = clipData.getItemAt(i);
                        Uri uri = item.getUri();
                        imagePaths.add(uri);
                    }
                }

                getToken();

            }
        }
        super.onActivityResult(requestCode, resultCode, data);
    }
    public void uploadMultipart(ArrayList<Uri> paths) {
        //getting name for the image

            //getting the actual path of the image

            //Uploading code
            try {
                String uploadId = UUID.randomUUID().toString();

                //Creating a multi part request
                MultipartUploadRequest multipartUploadRequest = new MultipartUploadRequest(this, uploadId, URL);
                for(int pathId=0;pathId<paths.size();pathId++) {
                    multipartUploadRequest.addFileToUpload(getPath(paths.get(pathId)), "image"+ pathId); //Adding file
                }
                Logger.setLogLevel(Logger.LogLevel.DEBUG);

                // Get Email Address from Shared Preferences
                SharedPreferences settings = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
                String email = settings.getString("email", "");

                Log.e("token", mToken);
                multipartUploadRequest
                        .addParameter("imagecnt", ""+paths.size()) //Adding text parameter to the request
                        .addParameter("email", email)
                        .addParameter("boc_acc_id", mAccount)
                        .addParameter("boc_sub_id", mSubscription)
                        .setNotificationConfig(new UploadNotificationConfig())
                        .setMaxRetries(2)
                        .startUpload(); //Starting the upload*/
            } catch (Exception exc) {
                exc.printStackTrace();
            }
    }

    //method to get the file path from uri
    public String getPath(Uri uri) {
        Cursor cursor = getContentResolver().query(uri, null, null, null, null);
        cursor.moveToFirst();
        String document_id = cursor.getString(0);
        document_id = document_id.substring(document_id.lastIndexOf(":") + 1);
        cursor.close();

        cursor = getContentResolver().query(
                android.provider.MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
                null, MediaStore.Images.Media._ID + " = ? ", new String[]{document_id}, null);
        cursor.moveToFirst();
        String path = cursor.getString(cursor.getColumnIndex(MediaStore.Images.Media.DATA));
        cursor.close();

        return path;
    }

    public void getToken(){
        OkHttpClient client = new OkHttpClient();
        Request request = new Request.Builder()
                .url(mUrlBase + "getToken")
                .build();
        Log.e("req", request.toString());
        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                Log.e("error", e.getMessage());
                e.printStackTrace();
            }

            @Override
            public void onResponse(Call call, final Response response) throws IOException {
                if (!response.isSuccessful()) {
                    Log.e("error", response.toString());
                    throw new IOException("Unexpected code " + response);

                } else {
                    mToken = response.body().string();
                    Log.e("token", mToken);
                    getSubscription();
                }
            }
        });

    }
    public void getSubscription(){
        OkHttpClient client = new OkHttpClient();
        Request request = new Request.Builder()
                .url(mUrlBase + "getSub?access_token=" + mToken)
                .build();
        Log.e("req", request.toString());
        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                Log.e("error", e.getMessage());
                e.printStackTrace();
            }

            @Override
            public void onResponse(Call call, final Response response) throws IOException {
                if (!response.isSuccessful()) {
                    Log.e("error", response.toString());
                    throw new IOException("Unexpected code " + response);

                } else {
                    String mUrl = response.body().string();
                    mSubscription = mUrl.substring(mUrl.length()-25);
                    Log.e("token", mSubscription);
                    redirectUser(mUrl);
                }
            }
        });

    }
    public void secondAuthentication(){
        OkHttpClient client = new OkHttpClient();
        Request request = new Request.Builder()
                .url(mUrlBase + "secondAuth?access_token=" + mToken + "&subId=" + mSubscription + "&code=" + mOath2)
                .build();
        Log.e("req", request.toString());
        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                Log.e("error", e.getMessage());
                e.printStackTrace();
            }

            @Override
            public void onResponse(Call call, final Response response) throws IOException {
                if (!response.isSuccessful()) {
                    Log.e("error", response.toString());
                    throw new IOException("Unexpected code " + response);

                } else {
                    String resp = response.body().string();
//                    mSubscription = mUrl.substring(mUrl.length()-25);
                    Log.e("token", resp);
                    try {
                        JSONObject json = new JSONObject(resp);
                        mAccount = ((JSONObject)(json.getJSONArray("selectedAccounts").get(0))).get("accountId").toString();
                        uploadMultipart(imagePaths);
                    } catch (JSONException e) {
                        e.printStackTrace();
                    }
//                    redirectUser(mUrl);
                }
            }
        });

    }

    public void redirectUser(String url){
        Intent i = new Intent(Intent.ACTION_VIEW);
        i.setData(Uri.parse(url));
        i.setAction(Intent.ACTION_VIEW);
        startActivityForResult(i, ONEBANK_REQUEST);
    }


}

