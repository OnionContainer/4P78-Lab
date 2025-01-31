import cv2
# import keras
# Load trained model
model = keras.models.load_model("tetris_shape_classifier.h5")



# Open document camera
# cap = cv2.VideoCapture(0)

def shape_update(shape_callback, cap):
    ret, frame = cap.read()
    if not ret:
        return

    # Preprocess the frame for prediction
    resized_frame = cv2.resize(frame, (64, 64))
    normalized_frame = resized_frame / 255.0
    input_frame = np.expand_dims(normalized_frame, axis=0)  # Reshape for model input

    # Predict shape
    predictions = model.predict(input_frame)
    shape_index = np.argmax(predictions)
    shape_labels = ["T-shape", "Z-shape", "L-shape"]
    detected_shape = shape_labels[shape_index]

    #add code
    mapping = [
        [0,2],
        [1,0],
        [2,1]
    ]

    report = mapping[shape_index]

    shape_callback(report)


    # Display result
    # cv2.putText(frame, detected_shape, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    # cv2.imshow("Real-time Tetris Shape Detection", frame)

    # # Press 'q' to exit
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break

# cap.release()
# cv2.destroyAllWindows()
