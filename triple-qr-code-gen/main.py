from kivy.app import App
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

from utils import create_tqr_image


def on_image_press(instance):
    app = App.get_running_app()
    app.change_image()


class ClickableImage(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_press=on_image_press)


class LimitedTextInput(TextInput):
    def __init__(self, min_length, max_length, **kwargs):
        super().__init__(**kwargs)
        self.min_length = min_length
        self.max_length = max_length

    def insert_text(self, substring, from_undo=False):
        if len(self.text) + len(substring) <= self.max_length:
            return super().insert_text(substring, from_undo=from_undo)

class TQRCodeGenApp(App):
    clickable_image = None
    text_ins = ["", "", ""]

    def build(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        for i in range(3):
            label = Label(text=f"Input {i + 1} (min: 1, max: 195):")
            layout.add_widget(label)
            text_input = LimitedTextInput(min_length=1, max_length=195, multiline=False)
            self.text_ins[i] = text_input
            layout.add_widget(text_input)

        self.clickable_image = ClickableImage(source='base_image.png', size_hint=(None, None), size=(300, 300))
        layout.add_widget(self.clickable_image)

        return layout

    def change_image(self):
        # access text inputs
        input_texts = [text_input.text for text_input in self.text_ins]
        # change image / make TQR
        if all(len(text) >= 1 for text in input_texts):  # check minimum length requirement
            self.clickable_image.texture = create_tqr_image(input_texts[0], input_texts[1], input_texts[2])
            self.clickable_image.fit_mode = "fill"
        else:
            print("One or more inputs do not meet the minimum length requirement.")

if __name__ == '__main__':
    TQRCodeGenApp().run()