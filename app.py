from flask import Flask, request, jsonify, send_file
import os
from moviepy.editor import VideoFileClip, vfx
from werkzeug.utils import secure_filename

app = Flask(__name__)
# נשנה את תיקיית השמירה לשולחן העבודה או תיקייה אחרת שנוחה לך
UPLOAD_FOLDER = r"C:\Users\zerem\Desktop\ProcessedVideos"
# ניצור את התיקייה אם היא לא קיימת
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def process_video(input_path, output_path, target_duration=59):
    clip = None
    processed_clip = None
    try:
        clip = VideoFileClip(input_path)
        processed_clip = clip.fx(vfx.speedx, final_duration=target_duration)
        processed_clip.write_videofile(output_path, codec="libx264")
        return True, f"Video processed successfully! Saved to {output_path}"
    except Exception as e:
        return False, str(e)
    finally:
        if clip is not None:
            clip.close()
        if processed_clip is not None:
            processed_clip.close()


@app.route('/process-video', methods=['POST'])
def process_video_endpoint():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400

    video_file = request.files['video']
    if video_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(video_file.filename)
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    output_filename = f"processed_{filename}"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

    video_file.save(input_path)

    success, message = process_video(input_path, output_path)

    try:
        if os.path.exists(input_path):
            os.remove(input_path)
    except Exception as e:
        print(f"Could not remove input file: {e}")

    if success:
        return jsonify({'message': message, 'output_path': output_path})
    else:
        return jsonify({'error': message}), 500


if __name__ == '__main__':
    app.run(debug=True)