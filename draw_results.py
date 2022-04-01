from matplotlib import pyplot
import numpy
import pandas

INITIAL_PARAMS = {'b', 'd', 'dd', 'sigma_m', 'sigma_w'}

PARAMS_NAMES = {'alpha': 'α', 'beta': 'β', 'gamma': 'γ'}

def get_parameter_grid(parameter, initial_parameters_data_frame):
  """
  Функция, возвращающая сетку значений определённого параметра, встречающегося в объекте pandas.DataFrame.
  @param parameter: str -- строковое имя требующегося параметра.
  @param initial_parameters_data_frame: pandas.DataFrame -- объект, в котором требуется найти значения параметров.
  @return Список из численных значений параметров.
  """
  result = []
  previous_value = initial_parameters_data_frame[0][parameter].item()
  for sample in initial_parameters_data_frame:
    current_value = sample[parameter].item()
    if result and (previous_value == current_value):
      continue
    elif result and (result[0] == current_value):
      break
    else:
      result.append(current_value)
      previous_value = current_value
  return result

def draw_parameter_plot(parameter, initial_parameter_1, initial_parameter_2, initial_parameters_data_frame, results_data_frame):
  """
  Функция, создающая график зависимости оптимального значения параметра трёхпараметрического замыкания от d и dd.
  @param parameter: str -- строковое имя параметра, для которого требуется построить график.
  @param initial_parameter_1: str -- строковое имя первого параметра (Oy), по значениям которого нужно строить сетку.
  @param initial_parameter_2: str -- строковое имя второго параметра (Ox), по значениям которого нужно строить сетку.
  @param initial_parameters_data_frame: pandas.DataFrame -- объект, содержащий информацию об исходных параметрах
    для симуляции и численного метода.
  @param results_data_frame: pandas.DataFrame -- объект, содержащий информацию о результатах работы метода поиска
    оптимальных параметров трёхпараметрического замыкания.
  @warning корректность работы функции очень сильно зависит от того, как располагаются сэмплы в dataframe;
    первый параметр размещается на оси y не просто так; будьте внимательны!
  """
  # В случае, когда мы строим график зависимости ошибки, выбираем более агрессивную палитру цветов.
  if (parameter in ('pop_error', 'error')):
    pyplot.style.use('classic')

  # Сетка биологического параметра по оси x.
  parameters_grid_x = get_parameter_grid(initial_parameter_2, initial_parameters_data_frame)
  # Сетка биологического параметра по оси y.
  parameters_grid_y = get_parameter_grid(initial_parameter_1, initial_parameters_data_frame)

  # Биологические параметры, по которым не строится сетка (они имеют константные значения).
  initial_parameters_left = INITIAL_PARAMS.copy()
  initial_parameters_left.remove(initial_parameter_1)
  initial_parameters_left.remove(initial_parameter_2)

  # Словарь соответствия между именем биологического параметра (по которому не строится сетка) и его константным значением.
  initial_parameters_left_values = {}
  for initial_parameter_left in initial_parameters_left:
    initial_parameters_left_values.update({initial_parameter_left: get_parameter_grid(initial_parameter_left, initial_parameters_data_frame)[0]})

  # Длина сетки по оси x.
  length_of_grid_x = len(parameters_grid_x)
  # Длина сетки по оси y.
  length_of_grid_y = len(parameters_grid_y)

  X, Y = numpy.meshgrid(numpy.array(parameters_grid_x), numpy.array(parameters_grid_y))

  z_list = list()
  i = 0
  while len(z_list) < length_of_grid_y:
    z_list.append([sample for sample in results_data_frame.loc[i:i+length_of_grid_x-1, parameter]])
    i += length_of_grid_x
  for v in z_list:
    while len(v) < length_of_grid_x:
      v.append(0.)

  Z = numpy.array(z_list)

  fig, ax = pyplot.subplots()
  pcm = ax.pcolor(X, Y, Z, shading='nearest')

  unique_suptitles = {'pop_error': 'Population error', 'pcf_error': 'PCF error'}
  if parameter in unique_suptitles:
    suptitle = unique_suptitles[parameter]
  else:
    suptitle = f'Optimal {PARAMS_NAMES[parameter]}'
  fig.suptitle(suptitle, fontsize=14, fontweight='bold')

  unique_colorbar_labels = {'pop_error': 'Relative value of difference between populations', 'pcf_error': 'Relative error of pcf norm'}
  if parameter in unique_colorbar_labels:
    colorbar_label = unique_colorbar_labels[parameter]
  else:
    colorbar_label = f'Optimal {PARAMS_NAMES[parameter]} value'
  fig.colorbar(pcm, ax=ax, label=colorbar_label)

  title = ''
  for parameter, value in initial_parameters_left_values.items():
    title += (parameter + '=' + str(value) + ' ')
  ax.set_title(title)
  ax.set_ylabel(initial_parameter_1 + ' value')
  ax.set_xlabel(initial_parameter_2 + ' value')

  pyplot.show()


COUNT_OF_DATA_FRAMES_TO_SHOW = 25

results = pandas.read_csv('./out_data/result.csv').fillna(method='bfill')
initial_parameters = [
  pandas.read_csv(f'./in_data/simulations_results/initial_parameters/{i}.csv')
  for i in range(1, COUNT_OF_DATA_FRAMES_TO_SHOW + 1)
]

draw_parameter_plot('alpha', 'sigma_m', 'sigma_w', initial_parameters, results)
draw_parameter_plot('beta', 'sigma_m', 'sigma_w', initial_parameters, results)
draw_parameter_plot('gamma', 'sigma_m', 'sigma_w', initial_parameters, results)
draw_parameter_plot('pop_error', 'sigma_m', 'sigma_w', initial_parameters, results)
draw_parameter_plot('pcf_error', 'sigma_m', 'sigma_w', initial_parameters, results)
