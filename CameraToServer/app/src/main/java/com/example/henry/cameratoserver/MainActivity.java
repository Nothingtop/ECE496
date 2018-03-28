    package com.example.henry.cameratoserver;

    import android.annotation.SuppressLint;
    import android.app.Activity;
    import android.content.ContentResolver;
    import android.content.ContentUris;
    import android.content.Context;
    import android.content.Intent;
    import android.database.Cursor;
    import android.graphics.Bitmap;
    import android.net.Uri;
    import android.os.Build;
    import android.os.Bundle;
    import android.os.Environment;
    import android.provider.DocumentsContract;
    import android.provider.MediaStore;
    import android.support.design.widget.FloatingActionButton;
    import android.support.design.widget.Snackbar;
    import android.support.v4.content.CursorLoader;
    import android.support.v4.content.FileProvider;
    import android.support.v7.app.AppCompatActivity;
    import android.support.v7.widget.Toolbar;
    import android.util.Log;
    import android.view.View;
    import android.view.Menu;
    import android.view.MenuItem;
    import android.widget.EditText;
    import android.widget.ImageView;
    import android.widget.Toast;

    import com.koushikdutta.async.future.Future;
    import com.koushikdutta.async.future.FutureCallback;
    import com.koushikdutta.ion.Ion;
    import com.koushikdutta.ion.Response;

    import org.apache.commons.io.IOUtils;
    import org.json.JSONException;
    import org.json.JSONObject;

    import java.io.File;
    import java.io.FileNotFoundException;
    import java.io.FileOutputStream;
    import java.io.IOException;
    import java.io.InputStream;
    import java.io.OutputStream;
    import java.net.URI;
    import java.net.URISyntaxException;
    import java.nio.file.FileStore;
    import java.text.SimpleDateFormat;
    import java.util.ArrayList;
    import java.util.Date;

    public class MainActivity extends AppCompatActivity {
        static final int REQUEST_IMAGE_CAPTURE = 1;
        private static final int TAKE_GALLERY = 2;
        String mCurrentPhotoPath;

        public class GenericFileProvider extends FileProvider {}

        @Override
        protected void onCreate(Bundle savedInstanceState) {
            super.onCreate(savedInstanceState);
            setContentView(R.layout.activity_main);
            Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
            setSupportActionBar(toolbar);

            FloatingActionButton fab = (FloatingActionButton) findViewById(R.id.fab);
            fab.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    takePhoto();
//                    pickImages();

                }
            });
        }

        public void takePhoto() {
//            Intent takePictureIntent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
//            if (takePictureIntent.resolveActivity(getPackageManager()) != null) {
//                startActivityForResult(takePictureIntent, REQUEST_IMAGE_CAPTURE);
//            }
            Intent takePictureIntent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
            // Ensure that there's a camera activity to handle the intent
            if (takePictureIntent.resolveActivity(getPackageManager()) != null) {
                // Create the File where the photo should go
                File photoFile = null;
                try {
                    photoFile = createImageFile();
                } catch (IOException ex) {
                    // Error occurred while creating the File
                }
                // Continue only if the File was successfully created
                if (photoFile != null) {
                    Uri photoURI = FileProvider.getUriForFile(this,
                            "com.example.android.fileprovider",
                            photoFile);
                    takePictureIntent.putExtra(MediaStore.EXTRA_OUTPUT, photoURI);
                    startActivityForResult(takePictureIntent, REQUEST_IMAGE_CAPTURE);
                }
            }
        }

        public void pickImages(){
            Intent intent = new Intent(); intent.setType("image/*");
            intent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, true);
            intent.setAction(Intent.ACTION_GET_CONTENT);
           startActivityForResult(Intent.createChooser(intent,"Select Picture"),TAKE_GALLERY);
    //        getDialog().dismiss();
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

            //noinspection SimplifiableIfStatement
            if (id == R.id.action_settings) {
                return true;
            }

            return super.onOptionsItemSelected(item);
        }

        @Override
        public void onActivityResult(int requestCode, int resultCode, Intent data) {
            super.onActivityResult(requestCode, resultCode, data);
            switch (requestCode) {
                case REQUEST_IMAGE_CAPTURE: {
                    if (resultCode == Activity.RESULT_OK) {
//                        Bundle extras = data.getExtras();
//                        Bitmap imageBitmap = (Bitmap) extras.get("data");
                        try {
                            uploadImage(new File(mCurrentPhotoPath));
                        } catch (Exception e) {
                            Toast.makeText(this, "Failed to load", Toast.LENGTH_SHORT)
                                    .show();
                            Log.e("Camera", e.toString());
                        }
                    }
                }
                case TAKE_GALLERY: {
                    if (resultCode == RESULT_OK) {
                        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.KITKAT && data != null) {
                            try {
                                Uri uri = data.getData();
//                                uploadImage(uri);
                            } catch (Exception e) {
                                Log.e("Pick Image Failed With:", e.getMessage());
                            }
                        }
                    } else if (resultCode == RESULT_CANCELED) {
                        // The user canceled the operation.
                    }
                }
            }
        }

        private File createImageFile() throws IOException {
            String timeStamp = new SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date());
            String imageFileName = "IMG_" + timeStamp + "_";
            File storageDir = getExternalFilesDir(Environment.DIRECTORY_PICTURES);
            File image = File.createTempFile(
                    imageFileName,  /* prefix */
                    ".jpg",         /* suffix */
                    storageDir      /* directory */
            );

            // Save a file: path for use with ACTION_VIEW intents
            mCurrentPhotoPath = image.getAbsolutePath();
            return image;
        }

        private File createImageFile(Bitmap bitmap) throws IOException {
            // Create an image file name
            String timeStamp = new SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date());
            String imageFileName = "IMG_" + timeStamp + "_";
            File storageDir = getExternalFilesDir(Environment.DIRECTORY_PICTURES);
            File image = File.createTempFile(
                    imageFileName,  /* prefix */
                    ".jpg",         /* suffix */
                    storageDir      /* directory */
            );

            OutputStream outputStream = new FileOutputStream(image);

            bitmap.compress(Bitmap.CompressFormat.PNG, 100, outputStream);
            // Save a file: path for use with ACTION_VIEW intents
            return image;
        }

        private void uploadImage(File im) {
            Future uploading = Ion.with(MainActivity.this)
                        .load("https://"
                                + ((EditText)findViewById(R.id.serverID)).getText().toString()
                                + ".ngrok.io/upload")
                        .setMultipartFile("image", im)
                        .asString()
                        .withResponse()
                        .setCallback(new FutureCallback<Response<String>>() {
                            @Override
                            public void onCompleted(Exception e, Response<String> result) {
                                try {
                                    JSONObject jobj = new JSONObject(result.getResult());
                                    Toast.makeText(getApplicationContext(), jobj.getString("response"), Toast.LENGTH_SHORT).show();
                                } catch (JSONException e1) {
                                    System.out.println(e1.getMessage());
                                }

                            }
                        });
        }
    }
