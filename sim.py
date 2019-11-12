import pandas as pd
import matplotlib.pyplot as plt
import numpy as np








if __name__ == "__main__":

    df = pd.DataFrame([])
    occ = pd.read_csv('//Users//Sami//Desktop//Super//Robotics//PARTICLE_FILTER//test_map.csv')

    prob = occ
    prob[prob == 0] = .1

    plt.ioff()
    plt.clf()
    plt.imshow(prob, 'Reds')  # This is probability
    #plt.imshow(occ, 'Greys')  # log probabilities (looks really cool)
    plt.show()

