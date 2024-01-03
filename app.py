from flask import Flask, render_template, request
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

def wrap_text(text, max_chars_per_line):
    words = text.split()
    lines = []
    current_line = ''
    for word in words:
        if len(current_line + ' ' + word) <= max_chars_per_line:
            current_line += ' ' + word
        else:
            lines.append(current_line.strip())
            current_line = word
    lines.append(current_line.strip())
    return '\n'.join(lines)

def process_video(video_path, text, font_size, font_color, outline_color='black'):
    video_clip = VideoFileClip(video_path)
    
    # Get the width of the video
    video_width = video_clip.size[0]

    # Calculate maximum characters per line based on video width and font size
    max_chars_per_line = int((video_width / 20) * (font_size / 50))  # Adjust the divisor to fit your desired length

    # Wrap the text to fit within the maximum characters per line
    wrapped_text = wrap_text(text, max_chars_per_line)

    # Calculate the position for the text (centered)
    txt_position = 'center'

    # Create text clips for the outline and main text
    outline_txt_clip = TextClip(
        wrapped_text,
        fontsize=font_size,
        color=outline_color,  # Set the outline color
        size=video_clip.size,
        align='center',
        bg_color='transparent',
        font='Amiri-Extrabold',
        kerning=-2,
        interline=-1
    )
    outline_txt_clip = outline_txt_clip.set_position(txt_position).set_duration(video_clip.duration)

    main_txt_clip = TextClip(
        wrapped_text,
        fontsize=font_size,
        color=font_color,  # Set the main text color
        size=video_clip.size,
        align='center',
        bg_color='transparent',
        font='Amiri-Extrabold',
        kerning=-2,
        interline=-1
    )
    main_txt_clip = main_txt_clip.set_position(txt_position).set_duration(video_clip.duration)

    # Create a composite video clip with the main text above the outline text
    result_clip = CompositeVideoClip([video_clip, outline_txt_clip.set_position((2, 2)), outline_txt_clip.set_position((-2, -2)),
                                      outline_txt_clip.set_position((-2, 2)), outline_txt_clip.set_position((2, -2)),
                                      main_txt_clip])

    # Save the result to a new file
    result_path = os.path.join(app.config['UPLOAD_FOLDER'], 'result.mp4')
    result_clip.write_videofile(result_path, codec="libx264", audio_codec="aac")

    return result_path, video_path



@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        video = request.files['video']
        text = request.form['text']
        font_size = int(request.form['font_size'])
        font_color = request.form['font_color']

        # Save the uploaded video
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], 'input_video.mp4')
        video.save(video_path)

        # Process the video and add text
        result_path, preview_path = process_video(video_path, text, font_size, font_color)

        return render_template('result.html', result_path=result_path, preview_path=preview_path)

    return render_template('index.html')

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    app.run(debug=True)
