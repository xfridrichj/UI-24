import tkinter as tk
import random
import copy


root=tk.Tk()
space=20;
max_x,max_y=600,600;
canvas=tk.Canvas(root, width=max_x, height=max_y);
canvas.pack()

#----------------------------------------------------------------------------
#GUI MRIEZKA

def read_matrix_file(filename):
    global num_treasures;

    with open(filename, 'r') as file:
        matrix_dimensions = file.readline().strip().split();
        X = int(matrix_dimensions[0]);  #number x
        Y = int(matrix_dimensions[1]);  #number y
        
        #starting position
        start_position=file.readline().strip().split();
        start_x=int(start_position[0]);  #starting x
        start_y=int(start_position[1]);  #starting y
        
        #number of treasures
        num_treasures=int(file.readline().strip());
        
        #treasure positions
        treasures=[]
        for t in range(num_treasures):
            treasure_position = file.readline().strip().split();
            treasure_x = int(treasure_position[0]);
            treasure_y = int(treasure_position[1]);
            treasures.append((treasure_x, treasure_y));
    return X, Y, (start_x, start_y), treasures;


def create_matrix(X, Y, start_position, treasures):
    #Initialize a 2D matrix with zeros
    matrix = [[0 for m in range(X)] for m in range(Y)];
    
    #Mark the starting position with 1
    start_x, start_y = start_position;
    matrix[start_y][start_x]=1;
    
    #Mark the treasures with 2
    for treasure in treasures:
        treasure_x, treasure_y=treasure;
        matrix[treasure_y][treasure_x]=2;
    
    return matrix

def create_grid(X,Y,matrix):
    for y in range(Y):
        for x in range (X):
            if matrix[y][x]==0:
                canvas.create_rectangle(space+tile*x,space+tile*y,space+tile*(x+1),space+tile*(y+1),fill="#09ba00");
            elif matrix[y][x]==1:
                canvas.create_rectangle(space+tile*x,space+tile*y,space+tile*(x+1),space+tile*(y+1),fill="#09ba00");
                canvas.create_text(space+tile*x+(tile//2),space+tile*y+(tile//2),text='S',font=("Arial",15,"bold"));
            else:
                canvas.create_rectangle(space+tile*x,space+tile*y,space+tile*(x+1),space+tile*(y+1),fill="#fccf03");


#volanie funkcii pre zobrazenie--------------------------------------------------------------------------------------
filename='start_ins.txt';
num_treasures=0;
#canvas.create_rectangle(space,space,max_x-space,max_y-space);
X, Y, start_position, treasures = read_matrix_file(filename);
start_x=start_position[0];
start_y=start_position[1];
tile=int(max_x-40)//X;

matrix = create_matrix(X, Y, start_position, treasures);
create_grid(X,Y,matrix);
root.mainloop();

#--------------------------------------------------------------------------------------------------------------------
#EVOLUCNY ALGORITMUS
ind_amm=int(input("Pocet jedincov:"));
#ind_amm=80;

num_gen=int(input("Pocet generacii:"));
#num_gen=300;

selection_input=int(input("Typ selekcie (0 - nahodny vyber, 1 - ruleta, 2 - turnaj) :"));
if selection_input not in [0,1,2]:
    print(f"Neplatny vstup selekcie ({selection_input}), vybrana selekcia je turnaj");

mut_rate=float(input("Sanca na mutaciu (%):"));
mut_rate=mut_rate/100;
#mut_rate=0.05;

num_elite=int(input("Pocet elitnych jedincov v generaciach (%):"));
num_elite=num_elite/100;
num_elite = int(ind_amm * num_elite);
#num_elite = int(ind_amm * 0.05);

num_cross=int(input("Pocet skrizenych jedincov v generaciach (%):"));
num_cross=num_cross/100;
num_cross = int(ind_amm * num_cross);
#num_cross = int(ind_amm * 0.8);

num_mut=int(input("Pocet zmutovanych jedincov v generaciach (%):"));
num_mut=num_mut/100;
num_mut = int(ind_amm * num_mut);  
#num_mut = int(ind_amm * 0.15);

if num_elite==0:
    num_old=ind_amm-num_cross-num_mut;
    #num_old = int(ind_amm * 0.05);
else:
    num_old=0;


num=list(range(ind_amm));

#arrays
temp_gen=[];

mut_indiv=[];

best_array=[];
best_keys_arr=[];
crossover_children=[];

postupnost=[];
arr_post=[];
fit_list=[];

new_gen=[];
new_fit_list=[];

pointer_ad=0;
ins_limit=0;


#pociatocna populacia
def ga_initial_pop(generation):
    for chromosones in range(ind_amm):
        population=[];

        for cells in range(64):
            random_value4cell=random.randrange(0,256);
            population.append(random_value4cell);

        generation.append(population);

    return generation;


#logika instrukcii
def vm_instructions(population):
    edited_pop=copy.deepcopy(population);

    global pointer_ad;
    global postupnost;
    
    bin_value ="{:0>8}".format(bin(population[pointer_ad])[2:]);

    ad_basedon_value=bin_value[2:8];
    ad_basedon_value_dec=int(ad_basedon_value,2);


    if bin_value[:2]=="00":
        pointer_ad+=1;
        if edited_pop[ad_basedon_value_dec]==255:
            edited_pop[ad_basedon_value_dec]=0;
        else:
            edited_pop[ad_basedon_value_dec]+=1;

    elif bin_value[:2]=="01":
        pointer_ad+=1;
        if edited_pop[ad_basedon_value_dec]==0:
            edited_pop[ad_basedon_value_dec]=255;
        else:
            edited_pop[ad_basedon_value_dec]-=1;

    elif bin_value[:2]=="10":
        pointer_ad=ad_basedon_value_dec;

    elif bin_value[:2]=="11":

        test="{:0>8}".format(bin(population[ad_basedon_value_dec])[2:])
        postupnost.append(vm_movemaker(test));
        #print(postupnost);
        
        pointer_ad+=1;  #pojde dalej 101 -> 110
    
    else:
        print(f"Error at {bin_value}\t{bin_value[:2]}");
    return edited_pop;

#logika vytvarania postupnosti
def vm_movemaker(bin_value):
    temp_onecounter=bin_value.count("1");
    if temp_onecounter<=2:
        ans='H';
    elif temp_onecounter==3 or temp_onecounter==4:
        ans='D';
    elif temp_onecounter==5 or temp_onecounter==6:
        ans='P';
    elif temp_onecounter==7 or temp_onecounter==8:
        ans='L';
    return ans;

def ga_finder(sequence,matrix):
    global start_x;
    global start_y;
    position_x=start_x;
    position_y=start_y;

    treasure=0;
    steps=0;
    penalty=0;

    ##print(sequence);
    i=0;
    while i != len(sequence):
        #print(sequence[i], position_x,position_y)
        if sequence[i]=='P':
            if position_x+1>6:
                penalty+=100;
                break;
            else:
                position_x+=1;
        elif sequence[i]=='L':
            if position_x-1<0:
                penalty+=100;
                break;
            else:
                position_x-=1;
        elif sequence[i]=='D':
            if position_y+1>6:
                penalty+=100;
                break;
            else:
                position_y+=1;
        elif sequence[i]=='H':
            if position_y-1<0:
                penalty+=100;
                break;
            else:
                position_y-=1;
        steps+=1;


        if matrix[position_y][position_x]==2:
            matrix[position_y][position_x]=3;
            treasure+=1;
        i+=1;
    return steps,treasure,penalty;


def ga_fitness(steps,treasure,penalty):
    global num_treasures;
    global found_all;
    #print(treasure);
    fit=round(1-float(steps/1000)+float(treasure),4)-penalty;
    if fit==1 and steps==0:
        fit=-100;
    if treasure==num_treasures and fit>0:
        #print(treasure,num_treasures);
        #print(fit);
        found_all=True;
    return fit;


def ga_biggest_num(dic, elite_size):
    global ind_amm;

    clone_dic={};
    clone_dic.clear();
    #clone_dic=copy.deepcopy(dic);
    return dict(sorted(dic.items(), key=lambda item: item[1], reverse=True)[:elite_size]);
    

def ga_random_selection(population, num_selections, children):
    for t in range(num_selections):
        parent1, parent2 = random.sample(population, 2);
        child = parent1[len(parent1) // 2:] + parent2[:len(parent2) // 2];
        children.append(child);

def ga_rulette_selection(population, fitness_scores, num_selections, children):
    total_fitness = sum(fitness_scores);
    selection_probs = [fitness / total_fitness for fitness in fitness_scores];

    for t in range(num_selections):
        parent1=random.choices(population, weights=selection_probs, k=1)[0];
        parent2=random.choices(population, weights=selection_probs, k=1)[0];

        child=parent1[:len(parent1)//2]+parent2[len(parent2)//2:];
        children.append(child);
    
    return children;

def ga_trnment_selection(population, fitness_scores, num_selections,children):
    for t in range(num_selections):
        tournament=random.sample(range(len(population)),2);
        best_chrom=max(tournament, key=lambda i: fitness_scores[i]);
        parent1=population[best_chrom];
        #print(f"parent1: {parent1}");
        
        tournament=random.sample(range(len(population)),2);
        best_chrom=max(tournament, key=lambda i: fitness_scores[i]);
        parent2=population[best_chrom];

        while parent1==parent2:
            tournament=random.sample(range(len(population)),2);
            best_chrom=max(tournament, key=lambda i: fitness_scores[i]);
            parent2=population[best_chrom];
        crossover_point1 = random.randint(1, len(parent1) // 3);
        crossover_point2 = random.randint(len(parent1) // 3, len(parent1) - 1);
        #child = parent1[:len(parent1) // 2] + parent2[len(parent2) // 2:];

        child = parent1[:crossover_point1] + parent2[crossover_point1:crossover_point2] + parent1[crossover_point2:];
        children.append(child);

def mut_rand_value(population, rate):
    temp_array=copy.deepcopy(population)

    for ind in range(len(population)):
        if random.random()<rate:
            rand_value_replace=random.randrange(0, 255);
            temp_array[ind]=rand_value_replace;
    return temp_array;

def mut_switch_add(population, rate):
    temp_array=copy.deepcopy(population);

    for ind in range(len(population)):
        if random.random()<rate:
            rand_ad_switch=random.randrange(0,64);
            while ind == rand_ad_switch:
                rand_ad_switch=random.randrange(0,64);
            temp_array[ind],temp_array[rand_ad_switch]=temp_array[rand_ad_switch],temp_array[ind];
    return temp_array;

def mut_invert_bits(population, rate):
    temp_array=copy.deepcopy(population);

    for ind in range(len(population)):
        if random.random()<rate:
            bin_chrom="{:0>8}".format(bin(temp_array[ind])[2:]);
            rev_bin=bin_chrom[::-1];
            temp_array[ind]=int(rev_bin,2);
            #print(population[ind], bin_chrom, rev_bin, int(rev_bin,2),temp_array[ind]);
    return temp_array;
def write_fit_trend_to_file(fit_trend, filename='data.txt'):
    with open(filename, 'a') as file:  # Open in append mode
        file.write(f'{fit_trend}\n')  # Write the fit trend value to the file
    #print(f'Fit trend {fit_trend} successfully written to {filename}')



#volanie funkcii------------------------------------------------------------------------------------------------------
ga_initial_pop(temp_gen);
best_fitness = -float('inf');
best_sequence = [];
#num_treasures=2;
con_after=False;
#loop
for gen in range(num_gen):
    print(f"==================== Generácia {gen} ====================")

    #reset matrix
    clone_gen = copy.deepcopy(temp_gen)
    found_all=False;
    con_choice=1;
    
    arr_post.clear()
    fit_list.clear()
    best_array.clear()
    best_keys_arr.clear()
    crossover_children.clear()
    mut_indiv.clear()


    for pop in range(ind_amm):
        for ins_limit in range(1000):
            #if pointer_ad>63:
            if pointer_ad>63 or len(postupnost)>500:
                break;
            clone_gen[pop] = vm_instructions(clone_gen[pop]);

        #print(postupnost);
        arr_post.append(postupnost)

        clone_matrix = copy.deepcopy(matrix);
        steps, treasure, penalty= ga_finder(postupnost, clone_matrix);

        #print(steps, treasure, penalty);
        fitness=ga_fitness(steps, treasure, penalty);
        fit_list.append(fitness);

        if fitness > best_fitness:
            best_fitness = fitness;
            best_sequence = postupnost.copy();

        if found_all==True and con_after==False:
            con_choice=int(input(f"Vsetky poklady najdene - {treasure} - chcete pokracovat? (0/1):"));
            if con_choice==0:
                break;
            else:
                con_after=True;
        postupnost.clear();
        pointer_ad = 0;
    #print(sorted(fit_list[:15],reverse=True));
    if con_choice==0:
        print("Koniec prehladavania");
        break;


    #Elitism
    zip_dic = dict(zip(num, fit_list))
    best_chrom = ga_biggest_num(zip_dic, num_elite)
    #print(best_chrom);

    fit_trend=round(sum(fit_list)/ind_amm,3);
    print(f"Fit trend: {fit_trend}");
    write_fit_trend_to_file(fit_trend)


    for key in best_chrom:
        best_keys_arr.append(key)
        best_array.append(temp_gen[key])

    #Add elite
    new_gen = best_array.copy();
    new_fit_list = [fit_list[key] for key in best_keys_arr];


    #Old gen
    old_gen = [temp_gen[i] for i in range(ind_amm) if i not in best_keys_arr]
    old_fit_list = [fit_list[i] for i in range(ind_amm) if i not in best_keys_arr]

    #Add non-elite
    oldies_c=random.sample(old_gen,num_old);
    for i in range(len(oldies_c)):
        new_gen.append(oldies_c[i]);


    #Crossover
    if selection_input==0:
        ga_random_selection(temp_gen,num_cross,crossover_children);
    elif selection_input==1:
        ga_rulette_selection(temp_gen, fit_list, num_cross,crossover_children);
    elif selection_input==2:
        ga_trnment_selection(temp_gen, fit_list, num_cross,crossover_children);
    else:
        ga_trnment_selection(temp_gen, fit_list, num_cross,crossover_children);
    new_gen += crossover_children;

    #Mutation
    mut_prep=[];
    mut_prep = random.sample(range(len(crossover_children)), num_mut)#indexy jedincov

    for child in mut_prep:
        mutated_child = mut_switch_add(crossover_children[child], mut_rate);
        #mutated_child = mut_rand_value(mutated_child, mut_rate);
        #mutated_child = mut_rand_value(crossover_children[child], mut_rate);
        mutated_child = mut_invert_bits(mutated_child, mut_rate);
        mut_indiv.append(mutated_child);
    new_gen += mut_indiv
    

    temp_gen.clear();
    temp_gen=copy.deepcopy(new_gen)

    mut_prep.clear()
    new_gen.clear()
    crossover_children.clear()
    mut_indiv.clear()
    best_chrom.clear();

print(f"Best Fitness: {best_fitness}");
print(f"Best Sequence of Moves: {best_sequence}");