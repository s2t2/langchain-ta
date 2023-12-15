

# todo: mechanism for allowing the user to specify their own homework questions
# hard coding our homework questions here for now :-)

#HOMEWORK_QUESTIONS = {
#    "Question 3.1 (LeNet Performance)":
#}

QUESTIONS = [
"""
+ Question 3.1 (LeNet Performance):
    What was the overall accuracy achieved by LeNet?
    Describe which classes generate the most errors based on the confusion matrix.
    What was the execution runtime?
    How many parameters does the model have?
""",
"""
+ Question 4.1 (Enhanced Classifier Performance):
    What was the overall accuracy achieved by the Enhanced Classifier?
    Describe which classes generate the most errors based on the confusion matrix.
    What was the execution runtime?
    How many parameters does the model have?
""",
"""
+ Question 6.1 (GoogLeNet Performance):
    What was the overall accuracy achieved by your implementation of GoogLeNet?
    Describe which classes generate the most errors based on the confusion matrix.
    What was the execution runtime?
    How many parameters does your model have?
""",
"""
+ Question 5.1 (Activations):
    For a given layer, describe why some activation channels (rows) tend to have stronger responses than other channels.
    (The strength of a response is visualized by the brightness of the image).
    Can you describe the textures that a channel is sensitive to?
    Do any channels have no activation response (all black images)? If so, why?
    Describe some differences in the layers. Why are the images getting smaller as the layers increase?
    What is the relationship between the layer and a receptive field?
    Why do the images have larger pixels at the higher levels making the image look more "pixelated"?
    Compare the activations between channels at a layer.
    Do the channels detect the same textures or do they detect different textures?
    What enables channels at the same layer to detect different textures?
""",
"""
+ Question 7.1 (Results Summary):
    Create a table of the methods you tried (LeNet, Enhanced Classifier, and GoogLeNet) with the overall accuracies.
    Which method provided the highest accuracy?
    Describe which architectural changes (number layers, channel sizes, learning rates, activation functions, etc.) had the strongest influence accuracy?
    Append the number of parameters and execution time for each model.
    Is the size and execution time correlated with accuracy?
""",
]

# [OPTIONAL grade points]
BONUS_QUESTIONS = [
"""
+ Bonus Question 4.1 A (Early Stopping):
    Create a keras callback function with early stopping instead of specifying the number of epochs, allowing the model to train until the patience parameter runs out.
    How many epochs did your model execute before early stopping quit?
""",
"""
+ Bonus Question 4.1 B (Learning Rate Scheduler):
    Add in a decaying learning rate scheduler to the optimizer, replacing the fixed-rate schedule.
    Example learning rate schedulers include: ExponentialDecay, PiecewiseConstantDecay, PolynomialDecay, InverseTimeDecay, CosineDecay, CosineDecayRestarts.
    What learninging rate decay did you apply? What were the parameters? Were there there any performance improvements?
""",
"""
+ Bonus Question 6.1 (Adapting GoogleNet Architecture):
    Make a changes to the original GoogLeNet architecture, such as the number of layers or types of layers that yields a consistent improvement in accuracy.
    (Not looking for a robust statistical test, just consistent improvement over two or more executions).
    To gain credit, you must describe your design change and demonstrate improved accuracy over two or more executions.

"""
]

ALL_QUESTIONS = QUESTIONS + BONUS_QUESTIONS

HOMEWORK_QUESTIONS = []
for question in ALL_QUESTIONS:
    question_id = question.split(")")[0]
    question_id = question_id.split("+")[-1].strip() + ")" #> "Bonus Question 6.1 (Adapting GoogleNet Architecture)"
    HOMEWORK_QUESTIONS.append((question_id, question))
