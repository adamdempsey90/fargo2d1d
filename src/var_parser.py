

def create_var_file(parfile):
# Grab default values
	with open('var.c','r') as f:
		lines = f.readlines()
	lines = [line for line in lines if 'var' in line]
	var_name_def =  [line.split('var("')[-1].split('"')[0] for line in lines]
	var_value_def = [line.split('");')[0].split(', "')[-1] for line in lines]

# Convert floats 
	var_value_def =  [float(val) if '.' in val and '/' not in val else val for val in var_value_def]

# Convert bools
	var_value_def = [bool(val) if val in ('YES','NO','yes','no','Yes','No') else val for val in var_value_def]


	params = {key:val for key,val in zip(var_name_def,var_value_def)}

# Get user parameters
	with open('../in/' + parfile) as f:
		lines = f.readlines()

	lines = [line.strip('\n').replace('\t',' ') for line in lines if '#' not in line]
	lines = [line for line in lines if line.strip() != '']
	par_key,par_val_str = zip(*[[val for val in line.split(' ') if val != '' ][:2] for line in lines])
	
	par_val=[]
	for val in par_val_str:
		try:
			val = float(val)
		except ValueError:
			pass
		par_val.append(val)
	
	par_val = [bool(val) if val in ('YES','NO','yes','no','Yes','No') else val for val in par_val]
	par_key = [key.upper() for key in par_key]
	
	for key,val in zip(par_key,par_val):
		params[key] = val

	with open('../' + params['OUTPUTDIR'] + 'variables.par','w') as f:
		lines = ['%s\t%s' % (key,str(val)) for key,val in params.items()]
		f.write('\n'.join(lines))  

if __name__ == '__main__':
	params = create_var_file('fast_test.par')
