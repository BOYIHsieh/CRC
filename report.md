# 实验一：Cache替换策略设计与分析 实验报告

### 计45 侯禺凡 2014011433

## 一、 实验目的

1. 深入理解各种不同的 Cache 替换策略
2. 理解学习不同替换策略对程序运行性能的影响
3. 动手实现自己的 Cache 替换策略

## 二、实验要求

1. 理解学习 LRU 及其它已经提出的 Cache 替换策略
2. 在提供的模拟器上实现 自己设计的 Cache 替换策略 
3. 通过 benchmark 测试比较不同的 Cache 替换策略  
4. 在实验报告中简要说明不同 Cache 替换策略的核心思想和算法  
5. 在实验报告中说明 自己是怎样对不同的 Cache 替换策略进行测试的  
6. 在实验报告中分析不同替换策略下，程序的运行时间、Cache 命中率受到的影响

## 三、提交文件

1. 模拟器CRC/src/LLCsim目录下的两个文件：replacement_state.cpp和replacement_state.h，位于本目录下
2. 实验报告（含“实验要求”的各项内容及实验数据），即本实验报告

## 四、传统Cache替换算法分析

### Random算法

Random算法是从Cache的一个组中随机找到一个块替换出去，没有充分利用数据的历史访问情况等特征，算法不确定性大，最坏情况很差。

### FIFO算法

先进先出算法的思路是先被加载的块先被换出去，算法优势在于具体实现较为简单（用一个队列维护Cache块换入顺序即可），并且时间开销较小，但是在缺失率方面表现较差。FIFO算法还存在belady现象。

### LRU算法

顾名思义，LRU算法就是选择最近最少使用的块替换出去。其主要动机是，最近未被使用的块很有可能今后都不会被使用。  

![](http://i.imgur.com/83rGp5w.png)

上图很好地说明了LRU算法的流程。图中每个块后面括号里的数表示上一次访问它的“时间”（这里时间用连续整数表示了）。可见，发生Cache缺失时，在所有块里找上次访问“时间”最小（也即最久没有被访问过）的块进行替换，而访问时则需要将被访问块括号里的数更新为当前“时间”即可。

LRU算法整体效果较好，但是对于某些访问顺序（例如刚刚被替换出去又访问该块）的效果很差。

### Pseudo-LRU(PLRU)算法

PLRU算法是对LRU算法的改进。通常，一个PLRU算法将Cache块组织为二叉树，这样搜索被替换的块的过程便可以转换为二叉树查找。其结构如下图：

![](http://i.imgur.com/P8wFjF4.png)

与LRU算法相比，PLRU算法使用了更少的存储空间，查找需要替换页面的时间也较短。

### Segmented LRU(SLRU)算法

在LRU算法中，有些数据在连续使用多次后，一段时间内不使用，但之后又连续使用多次，这样的数据显然是不太应该被被换出去的。为了改进LRU算法的这一缺陷，SLRU算法将每组内的Cache块分成两段，一段采取正常LRU算法，另一段作为reuse list，存放那些访问次数处于靠前的几位而不将其换出。

### LFU算法

如果一个数据在最近一段时间内使用次数很少，那么在将来一段时间内被使用的可能性也很小。基于这个思路，LFU算法每次选择访问次数最少的Cache块换出。

### Clock算法

在Clock算法里，维护着组中所有Cache块组织成的环状链表，以及指向链表中某项的指针，每个链表单元还设有访问位。当访问到Cache中存在的某个块时，将其访问位置为1。当Cache块缺失时，指针按固定方向在环上移动，若指向的链表项访问位为1，则将其置0，否则将其作为换出的Cache块并将指针移动到下一个链表项。

Clock算法在访问位这一设计上结合了LFU算法的思路，但是采取的环状链表结构使得其时间开销相比LFU算法降低不少。

## 五、自己设计的Cache替换算法

我设计的Cache替换算法我称之为**Two-Queue LRU**，或称**TQ-LRU**。在本实验报告第四部分谈到了LRU算法和LFU算法，同时注意到已给出的实验基本框架也实现了LRU算法，我便开始考虑对这两个传统算法进行改进。

### LRU、LFU存在的问题

LRU和LFU对于特定的访问情况不能很好地应对。若一个块访问多次后一段时间内不访问，接下来又进行多次访问，按照传统LRU算法这个块会被不停地换入换出，导致缺失率较高。若一个块访问多次后再也不被访问，按照传统LFU算法这个块将一直在Cache中，占用Cache空间间接导致其他Cache块被频繁换入换出。为了结合这两种算法的优点，摈弃缺点，我设计了TQ-LRU算法。

### TQ-LRU算法流程

在TQ-LRU中，维护着两个队列，记作A和B，队列A记录着被访问次数较低的那些Cache块，队列B则记录访问次数较高的那些。每个队列内部仍然采用传统LRU算法：若队列内部的Cache块被访问，则将其移动到队列尾端，表示刚刚被访问过。但是队列A和B也不是固定的，若队列A中有一个Cache块被访问次数变高（例如大于某个阈值），则将其放置到队列B的尾部，同时将队列B中被换出的Cache块移动到队列A的尾部作为刚被访问的块。更新队列的函数updateHYF()实现如下：

	void  CACHE_REPLACEMENT_STATE::UpdateHYF( UINT32 setIndex, INT32 updateWayID)
	{
	    LINE_REPLACEMENT_STATE *replSet = repl[ setIndex ];
	    UINT32 currLRUstackposition = replSet[updateWayID].LRUstackposition;
	    replSet[updateWayID].access_num ++;
	    if(currLRUstackposition < A_size)
	        //the chosen cache block is not protected, or in list A
	    {
	        if(replSet[updateWayID].access_num >= threshold)
	        //if(true)
	            //need added into protected
	        {
	            UINT32 protected_tail = -1;
	            for(UINT32 way = 0;way < assoc;way++)
	            {
	                if(replSet[way].LRUstackposition > currLRUstackposition
	                     && replSet[way].LRUstackposition < A_size)
	                    replSet[way].LRUstackposition--; //move cache block one by one
	                if(replSet[way].LRUstackposition == assoc - 1)
	                    protected_tail = way; //find the tail of list B
	            }
	            replSet[updateWayID].LRUstackposition = assoc - 1; //update stack pos
	            replSet[protected_tail].LRUstackposition = A_size - 1; //update stack pos
	            replSet[protected_tail].access_num = threshold - 1; //update access num
	        }
	        else
	        {
	            for(UINT32 way=0; way<assoc; way++) 
	            {
	                if( replSet[way].LRUstackposition > currLRUstackposition 
	                    && replSet[way].LRUstackposition < A_size - 1) 
	                {
	                    replSet[way].LRUstackposition--; //move cache block one by one
	                }
	            }
	            replSet[updateWayID].LRUstackposition = A_size - 1; //update stack pos
	        }
	    }
	    else
	        //protected, or list B
	    {
	        for(UINT32 way=0; way<assoc; way++) 
	        {
	            if( replSet[way].LRUstackposition > currLRUstackposition 
	                && replSet[way].LRUstackposition < assoc - 1) 
	            {
	                replSet[way].LRUstackposition--; //move cache block one by one
	            }
	        }
	        replSet[updateWayID].LRUstackposition = assoc - 1; //update stack pos
	    }
	}

而对于块不命中的情况，直接将队列A头部的（也即最久未使用的）Cache块换出即可，对应的Get_HYF_Victim()函数实现如下：

	INT32 CACHE_REPLACEMENT_STATE::Get_HYF_Victim(UINT32 setIndex)
	{
	    // Get pointer to replacement state of current set
	    LINE_REPLACEMENT_STATE *replSet = repl[ setIndex ];
	    INT32   lruWay   = 0;
	
	    // Search for victim whose stack position is assoc-1
	    for(UINT32 way=0; way<assoc; way++) 
	    {
	        if( replSet[way].LRUstackposition == 0 ) 
	        {
	            lruWay = way;
	            break;
	        }
	    }
	
	    // return lru way
	    replSet[lruWay].access_num = 0; //update access num
	    return lruWay;
	}

### TQ-LRU与LRU、LFU比较

TQ-LRU算法维护了两个队列A、B。队列A、B内部直接采取LRU算法，直接体现LRU的思想。而队列B里的块访问次数均大于队列A，队列B里的块要想被换出，首先要“降级”到队列A的尾部作为A中最近访问过的块，然后它要在一段时间内依然不被访问到，被队列A中的Cache块一点一点“挤出”队列，才能最终被选择为被换出的对象，于是体现了LFU访问次数越多越难被换出的思路。

另外，由于将Cache块划分为两个队列，每次访问Cache块时，只需要移动同一队列里的部分Cache块，另一个队列不需要移动或者只需要少量移动操作，可以预计相比LRU算法时间开销更小。

### 参数

TQ-LRU有两个可变参数：

    UINT32 protected_size;
    UINT32 threshold;

`protected_size`表示上面所述队列A的大小，`threshold`表示从Cache块队列A移动到队列B所需要的访问次数的阈值。经过尝试，我将`protected_size`取为Cache块路数的3/4，将`threshold`取为1，得到的结果在几次尝试中较好。当然，若这两个参数能够在执行过程中自适应地调整，或许能够取得更好的效果。

## 六、实验结果数据

为了进行对样例的测试，我写了两个python脚本，一个用来计时测试全部的样例并生成stat.gz文件，另一个则是用来统计stat.gz文件里的缺失率等信息。使用这两个脚本，我测试了Random算法的缺失率、普通LRU算法的缺失率，运行时间与CPI以及我的TQ-LRU算法的缺失率，运行时间与CPI。

下表列出了测试的缺失率、运行时间和CPI的结果。对每个测试样例，若TQ-LRU的缺失率比普通LRU更低，或者时间开销更低，都将其加粗注明。

由于随机算法具有很强的不确定性，一次运行的结果说服力较弱，因此不将其与我的算法相比较，仅作为一个参考。缺失率平均值用总缺失次数除以总访问次数来计算；运行时间以及CPI的平均值没有意义，因此不加列出。

|benchmark|RA Miss Rate(%)|LRU Miss Rate(%)|TQ-LRU Miss Rate(%)|LRU Time Spent(s)|TQ-LRU Time Spent(s)|LRU CPI|TQ-LRU CPI|
|--|--|--|--|--|--|--|--|
| 400.perlbench.out.trace.gz | 44.405676 | 40.795162 | 40.8223 | 25.363 | **16.285** | 0.642823 | 0.643058 |
| 401.bzip2.out.trace.gz | 61.678324 | 61.736905 | **61.618811** | 167.846 | **115.317** | 0.554642 | **0.553294** |
| 403.gcc.out.trace.gz | 45.639696 | 42.752104 | 45.22393 | 185.085 | **127.456** | 0.614864 | 0.62936 |
| 410.bwaves.out.trace.gz | 99.663413 | 99.663413 | 99.663413 | 167.16 | **112.399** | 0.253088 | 0.253088 |
| 416.gamess.out.trace.gz | 27.654574 | 26.32044 | 26.581533 | 168.051 | **117.983** | 0.30022 | 0.300688 |
| 429.mcf.out.trace.gz | 76.615176 | 75.676014 | **75.419172** | 210.574 | **143.206** | 2.55358 | 2.56828 |
| 433.milc.out.trace.gz | 76.274879 | 77.016366 | **74.65245** | 186.827 | **118.883** | 1.14939 | **1.12868** |
| 434.zeusmp.out.trace.gz | 82.6395 | 80.810031 | **80.776669** | 167.76 | **108.22** | 0.451633 | 0.451676 |
| 435.gromacs.out.trace.gz | 74.371936 | 71.197911 | 73.981483 | 180.116 | **120.693** | 0.607769 | 0.619842 |
| 436.cactusADM.out.trace.gz | 73.782369 | 76.116356 | **74.492258** | 175.446 | **115.164** | 0.44249 | **0.437274** |
| 437.leslie3d.out.trace.gz | 80.963942 | 84.028439 | 85.834731 | 185.428 | **121.294** | 1.50626 | 1.52264 |
| 444.namd.out.trace.gz | 66.312323 | 66.260327 | 66.260327 | 164.46 | **108.849** | 0.273795 | 0.273795 |
| 445.gobmk.out.trace.gz | 20.48383 | 14.918985 | 14.95012 | 188.319 | **127.315** | 0.383876 | 0.384057 |
| 447.dealII.out.trace.gz | 41.785592 | 45.089198 | **43.088454** | 190.75 | **133.04** | 0.463916 | **0.456639** |
| 450.soplex.out.trace.gz | 17.55362 | 15.201057 | **15.182479** | 104.194 | **74.984** | 0.356909 | **0.356844** |
| 453.povray.out.trace.gz | 40.20171 | 39.925829 | 39.930351 | 201.358 | **134.933** | 0.360431 | 0.360433 |
| 454.calculix.out.trace.gz | 38.31931 | 34.049964 | **34.045293** | 230.014 | **127.26** | 0.321346 | 0.321393 |
| 456.hmmer.out.trace.gz | 71.473643 | 71.473643 | 71.473643 | 224.193 | **133.72** | 0.258513 | 0.258513 |
| 458.sjeng.out.trace.gz | 94.103619 | 93.541479 | **93.495242** | 235.17 | **129.097** | 0.323006 | **0.32299** |
| 459.GemsFDTD.out.trace.gz | 84.152542 | 84.152542 | 84.152542 | 230.565 | **130.207** | 0.368143 | 0.368143 |
| 462.libquantum.out.trace.gz | 100.0 | 100.0 | 100.0 | 176.038 | **126.844** | 0.272749 | 0.272749 |
| 464.h264ref.out.trace.gz | 71.772141 | 70.008623 | 70.622752 | 169.949 | **124.295** | 0.28787 | 0.288684 |
| 465.tonto.out.trace.gz | 79.431374 | 78.869416 | **78.850367** | 152.012 | **108.55** | 0.347856 | **0.34785** |
| 470.lbm.out.trace.gz | 99.938533 | 99.972532 | **99.917986** | 182.375 | **141.946** | 1.15379 | **1.15329** |
| 471.omnetpp.out.trace.gz | 60.055683 | 59.444262 | 59.493394 | 186.282 | **150.804** | 0.41278 | **0.412774** |
| 473.astar.out.trace.gz | 5.847184 | 5.847184 | 5.847184 | 178.95 | **174.61** | 0.267647 | 0.267647 |
| 482.sphinx3.out.trace.gz | 97.261968 | 97.15598 | **97.147147** | 177.055 | **164.692** | 0.445644 | **0.445642** |
| 483.xalancbmk.out.trace.gz | 67.579471 | 66.27588 | **65.691579** | 194.357 | **175.043** | 0.414993 | **0.414414** |
| 999.specrand.out.trace.gz | 96.321177 | 95.9373 | **95.90531** | 113.308 | **101.777** | 0.336211 | 0.336211 |
| 总体平均 | 77.390039 | 77.319952 | **77.277251** | / | / | / | / |

## 七、实验结果分析

在全部29个样例（gz文件）中，我的TQ-LRU算法在14个样例上相比普通LRU算法而言降低了缺失率，有6个样例缺失率和普通LRU算法相同，只有9个效果更差。在全部29个样例的约1700万次cache查找中，采用TQ-LRU后的总体缺失率为77.2772%，相比普通LRU算法的77.3199%也有相当的改进。

相比缺失率，TQ-LRU算法在时间上的改进更加明显。在全部29个样例中，TQ-LRU算法的时间开销均低于LRU算法，且在有些样例上优化较大。**但是考虑到程序运行时间与计算机状态关系很大，加之我使用了虚拟机，不稳定性较大，因此我推测TQ-LRU算法在运行时间上的优势应该没有这么大**。

而对于CPI，在全部29个样例中，我的TQ-LRU算法在11个样例上相比普通LRU算法而言降低了缺失率，有7个样例缺失率和普通LRU算法相同，有11个效果更差。可见，在CPI上TQ-LRU算法相比普通LRU算法没有明显优势。

由上述几点对比可以发现，**TQ-LRU算法相比LRU算法，优化了缺失率，降低了运行时间，效果较好**，但在CPI上的改进则不甚明显。

## 八、结论

我设计了**基于双队列的TQ-LRU算法**，在LRU算法的基础上加入LFU算法的思想。TQ-LRU算法相比LRU算法，**优化了缺失率，也降低了运行时间，效果明显**，但在CPI上的改进则不甚明显。

## 参考资料

1. [维基百科：Cache replacement policies](https://en.wikipedia.org/wiki/Cache_replacement_policies)
2. [维基百科：Pseudo-LRU](https://en.wikipedia.org/wiki/Pseudo-LRU)
3. [维基百科：Least frequently used](https://en.wikipedia.org/wiki/Least_frequently_used)


