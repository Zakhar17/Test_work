from PIL import Image
import os
import argparse

folder = 'dev_dataset'


def image_comparison(folder):
    """Compares images in the folder"""

    Images = []
    for img in os.listdir(folder + "/."):
        # resize and greyshade
        i = Image.open(folder + '/' + img).resize((8, 8)).convert('L')
        # calc avarage pixel value
        pixel_map = i.load()
        pixel_sum = 0
        for x in range(i.size[0]):
            for y in range(i.size[1]):
                pixel_sum += pixel_map[x, y]

        avarage = pixel_sum / i.size[0] / i.size[1]

        # paint black or white
        ihash = ''
        for x in range(i.size[0]):
            for y in range(i.size[1]):
                if pixel_map[x, y] <= avarage:
                    pixel_map[x, y] = 255
                    ihash += '0'
                else:
                    pixel_map[x, y] = 0
                    ihash += '1'

        Images.append((img, ihash))


    def Hamming_dist(h0, h1):
        """Calculates the Hamming distance between 2 hashes"""

        d = 0
        for i in range(len(h0)):
            if h0[i] != h1[i]:
                d += 1
        return d


    i = 1
    print('\nFind identical and modified:\n')
    ident_and_modif_pairs = set()
    for img in Images:
        results = {'image': img[0], 'identical': [], 'modified': []}
        for compared in Images:
            if compared != img:
                d = Hamming_dist(img[1], compared[1])
                if d == 0:
                    results['identical'].append(compared[0])
                    ident_and_modif_pairs.add((img, compared[0]))
                elif 1 <= d <= 5:
                    results['modified'].append((compared[0], d))
                    ident_and_modif_pairs.add((img, compared[0]))


        print(f'{i})Image = {results["image"]}')
        print(f'identical = {results["identical"]}')
        print(f'modified = {results["modified"]}')
        print('\n')
        i += 1


    def find_similar(folder):

        """parameters"""

        kp_size = 9

        """main functions"""

        def Hamming_dist(h0, h1):
            """Calculates the Hamming distance between 2 hashes"""
            d = 0
            for i in range(len(h0)):
                if h0[i] != h1[i]:
                    d += 1
            return d

        def find_kp(image, radius=3, N=12, t=90):
            # algorithm
            i = Image.open(f'{folder}/{image}').convert('L')
            pixel_map = i.load()
            key_points = []

            for x in range(radius, i.size[0] - radius):
                for y in range(radius, i.size[1] - radius):

                    #         check main 4 points
                    center = pixel_map[x, y]
                    n, s = pixel_map[x, y - 3], pixel_map[x, y + 3]
                    w, e = pixel_map[x - 3, y], pixel_map[x + 3, y]
                    points = [n, s, w, e]

                    darker_points = list(filter(lambda p: center - t > p, points))
                    lighter_points = list(filter(lambda p: center + t < p, points))

                    if len(darker_points) >= 3 or len(lighter_points) >= 3:

                        #             check all 16 points
                        points.append(pixel_map[x - 3, y - 1])
                        points.append(pixel_map[x - 2, y - 2])
                        points.append(pixel_map[x - 1, y - 3])
                        points.append(pixel_map[x + 1, y - 3])
                        points.append(pixel_map[x + 2, y - 2])
                        points.append(pixel_map[x + 3, y - 1])
                        points.append(pixel_map[x + 3, y + 1])
                        points.append(pixel_map[x + 2, y + 2])
                        points.append(pixel_map[x + 1, y + 3])
                        points.append(pixel_map[x - 1, y + 3])
                        points.append(pixel_map[x - 2, y + 2])
                        points.append(pixel_map[x - 3, y + 1])

                        darker_points = list(filter(lambda p: center - t > p, points))
                        lighter_points = list(filter(lambda p: center + t < p, points))

                        if len(darker_points) >= N or len(lighter_points) >= N:
                            key_points.append((x, y))

            return [key_points, i]

        def create_kp_hash(image, kp, kp_size=kp_size):
            """Creates key point hash"""
            delta = int(kp_size / 2)
            x, y = kp[0], kp[1]
            area = (x - delta, y - delta, x + delta, y + delta)

            cropped_img = image.crop(area).convert('L')
            pixel_map = cropped_img.load()
            pixel_sum = 0

            for x in range(cropped_img.size[0]):
                for y in range(cropped_img.size[1]):
                    pixel_sum += pixel_map[x, y]

            avarage = pixel_sum / cropped_img.size[0] / cropped_img.size[1]

            # paint black or white
            ihash = ''
            for x in range(cropped_img.size[0]):
                for y in range(cropped_img.size[1]):
                    if pixel_map[x, y] <= avarage:
                        # pixel_map[x,y] = 255
                        ihash += '0'
                    else:
                        # pixel_map[x,y] = 0
                        ihash += '1'
            return ihash

        def check_similarity(kp_hashes1, kp_hashes2):

            n = 0

            for _hash in kp_hashes1:
                min_d = kp_size ** 2

                for comp_hash in kp_hashes2:
                    distance = Hamming_dist(_hash, comp_hash)

                    if distance < min_d:
                        min_d = distance

                if min_d <= 3:
                    n += 1
            return n

        """main algorithm"""

        images_kp = {}
        for img in os.listdir(folder + "/."):
            img_kp = find_kp(img)
            images_kp[img] = img_kp
            images_kp[img].append([create_kp_hash(img_kp[1], kp) for kp in img_kp[0]])
            # [0]-kp ([0]-x,[1]-y)
            # [1]-img
            # [2]-img hash
            print(f'{img} key points have been found!')

        for main_img in images_kp:
            for compared_img in images_kp:
                if main_img != compared_img and (main_img, compared_img) not in ident_and_modif_pairs:

                    kp_num = len(images_kp[main_img][0])
                    k = 1

                    if kp_num <= 10:
                        k = 0.5
                    elif 10 < kp_num <= 50:
                        k = 0.4
                    elif 50 < kp_num <= 100:
                        k = 0.3
                    elif 100 < kp_num:
                        k = 0.2

                    compared_kp_num = len(images_kp[compared_img][0])

                    if (1 - k) * compared_kp_num <= kp_num <= (1 + k) * compared_kp_num:

                        n = check_similarity(images_kp[main_img][2], images_kp[compared_img][2])
                        coef = 0.14 * (kp_num + compared_kp_num) / 2
                        if n >= coef:
                            print(f'\n{main_img} is similar to {compared_img} with n = {n}, low_bound = {coef}')
                            ident_and_modif_pairs.add((main_img, compared_img))
                            ident_and_modif_pairs.add((compared_img, main_img))

        print('\n end! All similar pairs found!')

    print("\n Now algorithm will search for similar photos")
    print("Be aware that it may take time until \n key points are found on all images")
    print("Photos of big size slower the algorithm. In new versions algorithm speed will improve!")

    find_similar(folder)


parser = argparse.ArgumentParser(description='Compare images')
parser.add_argument('--path', dest='PATH', action='store', help='Write your path to the photos directory')

args = parser.parse_args()

if args.PATH is not None:
    image_comparison(args.PATH)
