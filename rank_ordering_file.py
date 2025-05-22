import numpy as np

# assumes block:cyclic assigment of MPI ranks

repeat = 2
num_nalu_ranks_per_node = 55
num_amr_ranks_per_node = 8

num_nalu_ranks = num_nalu_ranks_per_node * repeat # assume same number of nalu ranks every node
num_amr_ranks = num_amr_ranks_per_node * repeat # assume same number of amr ranks every node
total_ranks = num_nalu_ranks + num_amr_ranks

num_L3 = 8
cores_per_L3 = 8
node_size = num_L3 * cores_per_L3
exclude_core = np.array([0]) # core to exclude
exclude_core_repeated = [0]
for r in range(repeat):
    for val in exclude_core:
        exclude_core_repeated.append(val + r * node_size)
print(exclude_core_repeated)

print(num_nalu_ranks_per_node + num_amr_ranks_per_node + exclude_core.size)
assert (num_nalu_ranks_per_node + num_amr_ranks_per_node + exclude_core.size == node_size)

cores_cyclic = np.zeros(node_size).astype(int)
for i in range(num_L3):
  for j in range(cores_per_L3):
    cores_cyclic[j*num_L3 + i] = i*cores_per_L3 + j

cores_cyclic_repeated = []
for i in range(repeat):
  cores_cyclic_repeated.append(cores_cyclic + i * node_size)
cores_cyclic_repeated = np.concatenate(cores_cyclic_repeated)
# print(cores_cyclic_repeated)

amr_ranks = np.arange(num_amr_ranks)
# print(amr_ranks)

nalu_ranks = np.arange(num_amr_ranks, total_ranks, 1)
# print(nalu_ranks)

mpi_cyclic = np.zeros(node_size * repeat).astype(int) - 1 # fill with -1

for i in range(repeat):
  block_start = i * node_size
  block_end = block_start + node_size
  
  block_cores = cores_cyclic_repeated[block_start:block_end]
  # print(block_cores)
  
  # put amr on last 8 cores in the cyclic assignment
  amr_cores = block_cores[-num_amr_ranks_per_node:]
  # print(amr_cores)
  
  amr_core_positions_in_block = np.where(np.isin(block_cores, amr_cores))[0]
  amr_indices_in_mpi_cyclic = block_start + amr_core_positions_in_block
  mpi_cyclic[amr_indices_in_mpi_cyclic] = amr_ranks[i * num_amr_ranks_per_node : (i + 1) * num_amr_ranks_per_node]

  # NALU cores: all except last 8 and excluded core
  nalu_cores_candidates = block_cores[:-num_amr_ranks_per_node]
  print(nalu_cores_candidates)
  nalu_cores = np.array([core for core in nalu_cores_candidates if core not in exclude_core_repeated])
  nalu_cores_sorted = np.sort(nalu_cores)
  # print(nalu_cores)
  # print(nalu_cores_sorted)
  
  nalu_ranks_block = nalu_ranks[i * num_nalu_ranks_per_node : (i + 1) * num_nalu_ranks_per_node]
  # print(nalu_ranks_block)
  
  # Assign NALU ranks
  j = 0 + node_size * i
  for core in nalu_cores_candidates:
    if core in exclude_core_repeated:
      j=j+1
      continue
    # print(core)
    k = np.where(nalu_cores_sorted == core)
    # k = np.where(nalu_cores_sorted == nalu_cores_sorted[j])
    mpi_cyclic[j] = nalu_ranks_block[k]
    j=j+1

  print(mpi_cyclic)

flat_str_arr = np.where(mpi_cyclic.flatten() == -1, '', mpi_cyclic.flatten().astype(str))
rank_reorder = ','.join(flat_str_arr)
print(rank_reorder)


