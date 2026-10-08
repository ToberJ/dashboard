"""Build the guitar project page from reviewed plans and saved experiment reports.

Run from the project root: source env.sh && python website/build_guitar_dashboard.py
Only the guitar page/assets and its hub entry are changed. No simulation runs.
"""
from pathlib import Path
import html
import json
import shutil
import hashlib
import argparse

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--project-root', type=Path, default=Path(__file__).resolve().parents[4])
args = parser.parse_args()
ROOT = args.project_root.resolve()
SITE = Path(__file__).resolve().parents[2]
ASSETS = SITE / 'assets/guitar'
ASSETS.mkdir(parents=True, exist_ok=True)

# Reviewed full C-to-D v1 diagnostic; retain failure label, not a milestone pass.
cd_folder = ROOT / 'analysis/dual_chord_pick_v1/dual_nominal_v1'
for src, dst in [('preview.mp4','c-to-d-dual_nominal_v1.mp4'),('preview.png','c-to-d-dual_nominal_v1.png')]:
    shutil.copy2(cd_folder/src, ASSETS/dst)

# Complete v2 diagnostic; contact failures retained.
cd_v2 = ROOT / 'analysis/dual_chord_pick_v1/dual_velocity_v2'
for ext in ['mp4','png']:
    shutil.copy2(cd_v2/f'preview.{ext}', ASSETS/f'c-to-d-dual_velocity_v2.{ext}')

# Publish only the completed and visually reviewed v4 video.
cd_v4 = ROOT / 'analysis/dual_chord_pick_v1/dual_candidate_v4'
review_v4 = json.loads((cd_v4/'review.json').read_text())
assert review_v4.get('visual_review') == 'reviewed', 'Wait for complete v4 media review before building'
for ext in ['mp4','png']:
    shutil.copy2(cd_v4/f'preview.{ext}', ASSETS/f'c-to-d-dual_candidate_v4.{ext}')

def read(path): return json.loads((ROOT/path).read_text())
def esc(value): return html.escape(str(value), quote=True)

suite = read('analysis/mentor_contact_targets/shared_release_suite_v2_report.json')
manifest = read('retarget/contact_labels/shared_multifinger_release_suite_v2.json')
assert suite['all_passed'] and suite['same_compiled_guitar']
assert len(manifest['tasks']) == len(suite['tasks']) == 5
assert suite['completed_runs'] == suite['required_runs'] == 20
phases = [
    dict(id='foundation', n='01', title='建立可信的仿真与数据基础', status='done', tag='已有基础',
         goal='统一人手、机器人手和吉他的坐标与物理模型，让失败能够被观察、复现。',
         deliverable='Wuji Hand 2 模型、MoCap 映射、共用吉他配置、每步接触与力矩审计。',
         gate='当前基础已用于小集回归；指腹、接触参数和真实吉他标定仍是独立待办。'),
    dict(id='baseline', n='02', title='有接触目标的左手多指基准', status='scoped', tag='限定范围通过',
         goal='保留 dataset 动作与指定指法，在动力学里完成多指按弦、保持与部分释放。',
         deliverable='C / F / A / Bb / D 五个片段、20 项回归、轨迹与多视角视频。',
         gate='当前 20/20 通过；按片段调过参数，使用人工接触候选，并不代表任意动作自动成功。'),
    dict(id='inference', n='03', title='减少逐片段人工标注', status='planned', tag='连续转换基线之后',
         goal='从 MoCap 提出每指的弦、品、接触区间候选，让不确定性显式可见。',
         deliverable='标定依赖清单、冻结的开发／留出拆分、候选标签与人工核对记录。',
         gate='在 2–3 段未调参的非横按动作上检验；报告错误与拒判，不能用测试答案反推 offset。'),
    dict(id='sequence', n='04', title='连续动作与未见片段', status='next', tag='当前：C→D 连续转换',
         goal='从“按住一个姿态”走向连续按下、释放、换指与换位。',
         deliverable='连续 retarget、接触状态切换、原速／降速结果、失败分类与批量数据索引。',
         gate='完整区间验收；开发集与留出集分开，明确速度和初始化条件，不只截取成功画面。'),
    dict(id='plucking', n='05', title='右手拨弦与发声验证', status='planned', tag='物理线并行准备',
         goal='建立真正的拨弦、弦振动与发声评价，区分“有接触力”和“能弹出目标音”。',
         deliverable='拨片／指拨方案对照、单弦释放振动、音高／起音／串扰评测。',
         gate='拨弦由驱动和接触产生；声音分析或合成由物理振动驱动，验证按弦在拨动后仍有效。'),
    dict(id='bimanual', n='06', title='双手协同与可泛化控制', status='planned', tag='方法待实验选择',
         goal='左手准备好接触，右手在正确时刻拨弦；从可执行轨迹走向可适应控制。',
         deliverable='双手时间同步、固定轨迹控制基线、模仿／残差控制／RL 对照。',
         gate='在未见动作、时序偏移和扰动下评估双手成功率；尚未选定最终 policy 方法。'),
    dict(id='hardware', n='07', title='G1 集成与 sim-to-real', status='planned', tag='后续',
         goal='把两只手接到 G1，逐级验证实际安装、支撑、驱动与物理参数。',
         deliverable='硬件尺寸与限幅、手臂／手腕集成、参数辨识、台架到双手的分级实验。',
         gate='先台架单指、再左手、右手与双手；真实观测与仿真对照，不把虚拟腕成功当作 G1 结果。'),
    dict(id='research', n='08', title='形成可检验的研究贡献', status='planned', tag='评测设计提前做',
         goal='用明确问题、可靠基线、消融和失败边界支撑 robotics 论文。',
         deliverable='任务定义、数据拆分、方法对照、物理与真机证据、可复现材料。',
         gate='贡献由实验支持；不预设论文结论，不把人工目标或合成音频当原始人类真值。'),
]

# Status records describe evidence, not active processes or estimates of time.
tasks = []
def task(id, phase, title, status, priority, lane, detail, accept, depends=()):
    tasks.append(dict(id=id, phase=phase, title=title, status=status, priority=priority,
                      lane=lane, detail=detail, accept=accept, depends=list(depends)))
task('FND-01','foundation','选定 Wuji Hand 2，保留换手配置入口','done','P0','基础','已比较手型并选用 Wuji Hand 2；Beta1／Beta2 需要核对实际硬件。','模型选择有依据；真机版本单独确认。')
task('FND-02','foundation','统一坐标、手性与弦号','done','P0','Retarget','镜像变换与弦序已统一修正。用户弦号从粗到细 1–6。','使用一致映射；1=低 E，2=A，3=D，4=G，5=B，6=高 E。')
task('FND-03','foundation','统一吉他网格、质量、张力与阻尼配置','done','P0','物理','五段使用相同吉他模型；阻尼按代表弦长分配，细化不偷偷增加总阻尼。','实际编译模型的 guitar signature 一致；不把它当空间收敛证明。')
task('FND-04','foundation','建立每积分步接触审计','done','P0','评测','已检查正确手指、弦–品丝力、邻弦、刚体、自碰、穿透及驱动限幅。','失败不能被截图、平均值或只看手–弦接触掩盖。')
task('BASE-01','baseline','完成五片段、20 项多指回归','done','P0','Retarget','正常、半时间步、两组 gain/reset，每片段四项。C／D 含释放，其他是保持子任务。','当前冻结版本 20/20 通过；保留失败对照。',('FND-02','FND-03','FND-04'))
task('BASE-02','baseline','修复 F 无名指高负载与关节偏差','done','P0','Retarget','同指／同弦／同品内修正落点，降低前馈；完成落点×力的受控比较与加密参考回归。','末关节 RMS 11.68°→0.40°；四指接触通过，电机限幅未增加。',('BASE-01',))
task('BASE-03','baseline','保存复现输入、结果与可视化','done','P1','评测','参考轨迹、模型、运行参数、报告 hash、多视角视频与源码快照已保存。','从冻结清单复查结果，并区别 raw、IK 与实际动力学。',('BASE-01',))
task('BASE-04','baseline','跟踪 A 的指腹位置偏差','open','P1','Retarget','几何目标最大误差 4.24 mm；真实保持主要剩沿颈约 3 mm 偏差。加权与八初值诊断无实质改善。','先确定误差来源和可接受姿态；不降低碰撞标准、不移动标签来美化分数。',('BASE-01',))
task('INF-01','inference','盘点人工标签与标定之间的依赖','next','P0','Retarget','逐项标明腕先验、指甲→指腹 offset、弦／品选择、按压区间来自哪里。','区分可迁移标定与答案相关标定；留出集的标签不参与参数拟合。',('BASE-03',))
task('INF-02','inference','确定开发集与 2–3 段非横按留出片段','planned','P0','评测','先看 raw 动作质量与接触转换；E/G 可重新检查，但不靠文件名指定指法。','记录片段、缺失／跳点、速度、选择理由，实验前冻结拆分。',('INF-01',))
task('INF-03','inference','生成每指弦／品／时段候选','planned','P0','Retarget','结合几何、运动连续性和接触约束提出候选；指甲高度不能直接当接触真值。','给出候选、置信信息与 unknown 区间；保留歧义，不强制每帧有答案。',('INF-01','INF-02'))
task('INF-04','inference','人工核对候选并建立版本记录','planned','P0','人工复核','用 raw marker、目标和机器人姿态的多视角对照，核对手指身份与明显不合理的切换。','记录接受／修改／无法判断；人工候选仍不冒充录制时的接触真值。',('INF-03',))
task('INF-05','inference','未调参片段的物理闭环验证','planned','P0','评测','沿用同一吉他、驱动上限和完整区间检查，报告源速度与初始化。','逐段报告成功、失败和拒判；测试失败若用于调参，就重新划分验证集。',('INF-04',))
task('SEQ-01','sequence','覆盖按下—保持—释放—再按下','next','P0','Retarget','C→D 候选接触任务连续执行：单次初始化、规划过渡、不重置。名义时间步已通过；减半时间步结果见下方独立证据。','每次转换都检查目标品丝力、动作连续性、邻弦、异常冲击和关节跟踪；单个转换不代表未见序列泛化。',('BASE-03',))
task('SEQ-02','sequence','验证原速与必要的速度缩放','planned','P1','控制','当前 A=0.4×、D=0.5×；原速能力仍需单独测量。','原速和慢速分开报告，动作保真与物理可执行性同时检验。',('SEQ-01',))
task('SEQ-03','sequence','可恢复的批量 retarget 与质量筛选','planned','P1','数据','本地数据目录有 50 个 CSV；它们尚未全部 retarget／验证。','保存原始索引、配置、标签来源、失败原因和版本；只将合格轨迹进入后续训练。',('INF-05','SEQ-01'))
task('SEQ-04','sequence','学习或规划完整接近与握颈','planned','P2','控制','当前初始化含几何摆姿态和程序加载，不是完整从远处接近任务。','从明确初始状态通过动力学接近、握颈并切入按弦，不靠逐帧写状态。',('SEQ-01',))
task('PHY-01','foundation','测量指腹与接触模型参数','planned','P1','物理','刚性指腹、接触刚度和摩擦尚未真机标定；仿真接触成功不等于 sim-to-real。','获取可复查测量或区间；做参数敏感性与失败边界。',('FND-01',))
task('PHY-02','foundation','检验弦空间离散与动力学收敛','next','P1','物理','半时间步已经检验；共同网格并不证明空间收敛。','固定总质量、张力、总阻尼，对照网格；报告接触力和振动差异。',('FND-03',))
task('PHY-03','foundation','核对实体吉他与硬件尺寸','planned','P1','硬件','确认 Wuji 2 硬件版本、指腹尺寸、吉他弦距／action／颈厚。宽琴颈是候选，不是现已更换的模型。','记录实测值和模型差异；换琴必须重新验证相关任务。',('FND-01',))
task('RH-01','plucking','比较拨片与直接指拨','planned','P1','物理','右手方案尚未决定；先设计最小单弦实验。','比较可达性、可靠脱弦、串扰与真机装配，再决定方案。',('PHY-01',))
task('RH-02','plucking','单弦真实接触拨动与自由振动','planned','P1','物理','受限驱动让拨片／手指接触弦并脱离，不脚本强制弦形变。','检查拨动时刻、力与振动；实验重复且没有持续粘连或数值能量异常。',('RH-01','PHY-02'))
task('RH-03','plucking','建立音高、起音、衰减与串扰指标','planned','P1','评测','声音来自物理振动的分析／合成；录制数据没有逐帧音频真值。','区分接触、振动、声音三个成功层次，并验证目标音与邻弦输出。',('RH-02',))
task('RH-04','plucking','拨动扰动下验证左手按弦','planned','P1','双手','目前左手检查并未证明所有按弦都能承受右手拨动并清晰发音。','拨动后目标品丝终止仍有效；记录打品、失接触和误音。',('RH-02','INF-05'))
task('BI-01','bimanual','双手动作与接触事件同步','planned','P1','双手','建立左手就绪／保持、右手接触／脱弦的时间关系。','先完成一组音，再做短序列；报告时序误差和双手联合成功。',('SEQ-01','RH-04'))
task('BI-02','bimanual','建立控制与学习方法对照','planned','P1','学习','先用可执行轨迹控制作基线，再比较模仿、接触反馈／残差与 RL；不预设最终方法。','相同观测、任务和预算比较；不以人为调整每段的结果代替泛化。',('BI-01','SEQ-03'))
task('BI-03','bimanual','未见序列与接触扰动评测','planned','P1','评测','测试动作顺序、时序、标定误差和物理参数变化；开发与测试隔离。','报告多次试验、失败类型与适用范围，保留全部失败。',('BI-02',))
task('HW-01','hardware','确认双手安装、通信与真实限幅','planned','P1','硬件','两只手最终装在 G1；目前虚拟腕不代表 G1 手臂支撑。','硬件版本、安装变换、驱动接口、量程及停止条件有实测记录。',('PHY-03',))
task('HW-02','hardware','将虚拟腕替换为 G1 手臂／支撑模型','planned','P1','硬件','加入真实可达性、手腕负载与吉他固定方式。','全模型可执行参考，支撑力与关节限制一致，明确外部夹具。',('HW-01','SEQ-01'))
task('HW-03','hardware','台架单指到左手的参数辨识','planned','P1','硬件','从低复杂度实验核对真实按压力、形变、tracking 与模拟差异。','先单指，再多指与释放；用真实测量修正模型。',('PHY-01','HW-01'))
task('HW-04','hardware','右手、双手与 G1 实机演示','planned','P2','硬件','只有前序模块通过，才逐级组合右手拨弦、双手短序列和 G1。','发布完整过程及失败，记录真实声音与实际接触／驱动观测。',('HW-02','HW-03','RH-03','BI-03'))
task('RES-01','research','提前定义研究问题、基线与指标','next','P1','研究','候选问题：怎样将人手动作转为具有真实接触、可执行且可泛化的双手控制？','写清现有方法差距、待验证假设与可反驳的实验；贡献尚未定论。',('BASE-03',))
task('RES-02','research','做 retarget／接触／控制消融','planned','P1','研究','比较纯 marker IK、接触约束、力控制、时间采样和人工校正的作用。','一次区分一个因素；相同模型与评价条件，公开失败与人工介入量。',('INF-05','BI-02'))
task('RES-03','research','整理复现、数据许可与公开材料','planned','P2','研究','保存版本化配置、指标、视频和实验协议；原始 dataset 不在此网站重新分发。','核对上游许可与演示／数据发布范围，发布可复现且归属清楚的材料。',('RES-02',))
task('RES-04','research','论文与最终项目演示','planned','P2','研究','目标是 robotics 会议；投稿 venue、时间与最终贡献尚未决定。','论文结论与完整证据一致；真实实验、仿真和概念计划分别标明。',('HW-04','RES-03'))
task('LATER-01','baseline','F 完整食指横按与完整和弦','deferred','P2','Retarget','用户决定后置。现有四指尖测试保留，不扩成已验证六弦 F 的说法。','未来单独定义食指多处接触、全部目标弦与发声验收。',('SEQ-01',))
task('LATER-02','sequence','高难把位、横按与长曲目','deferred','P2','双手','先完成非横按短序列和可检验的泛化，再增加难度。','按新增接触模式逐级扩展，不能从短片段通过推断长曲目成功。',('BI-03',))

titles = {'ChordC':'三指按弦与分步释放','ChordF':'四指尖保持 · 不含横按','ChordA':'相邻弦三指保持','ChordBb':'四指保持子任务','ChordD':'四指保持与释放'}
clips = []
for task_spec, audited in zip(manifest['tasks'], suite['tasks']):
    assert task_spec['tag'] == audited['tag'], 'Manifest/report order mismatch'
    folder=ROOT/'retarget/out/mentor_sequence'/task_spec['tag']
    plan=json.loads((folder/'plan_report.json').read_text())
    run=json.loads((folder/'run_report_5e-06.json').read_text())
    name=plan['source']; key=name.replace('Chord','').lower()
    for src_name,dst_name in [('multiview.mp4',f'{key}.mp4'),('multiview_still.png',f'{key}.png')]:
        shutil.copy2(folder/src_name, ASSETS/dst_name)
    clips.append(dict(id=key,name=name,title=titles[name],sourceFrames=[plan['frame_start'],plan['frame_end']],
        fingers=len(plan['multi_contacts']),speed=1/task_spec['playback_scale'],passed=audited['passed'],
        cases=[dict(name=r['case'],passed=r['passed']) for r in audited['runs']],
        video=f'../assets/guitar/{key}.mp4',poster=f'../assets/guitar/{key}.png',
        initialization=('包含 0.8 s 程序驱动加载，之后为 dataset 参考动作。' if run['ramp_from_reset'] else '采用几何初始化与稳定阶段；不代表完整从远处接近。'),
        meanFretForces=[round(c['mean_fret_force_N'],4) for c in run['multi_contact_evaluation']['contacts']],
        contacts=[dict(finger=c['finger'],string=c['user_string'],fret=c['fret']) for c in plan['multi_contacts']],
        convergencePercent=round(audited['convergence']['maximum_mean_fret_relative_difference']*100,4)))
transition_folder=ROOT/'retarget/out/mentor_sequence/Transition_C_D_v4_vertical'
transition=read('retarget/out/mentor_sequence/Transition_C_D_v4_vertical/transition_acceptance_5e-06.json')
comparison_path=transition_folder/'transition_summary.json'
comparison=json.loads(comparison_path.read_text()) if comparison_path.exists() else None
transition_state='两种时间步均通过，力收敛检查通过' if comparison and comparison['passed'] else '名义时间步通过；减半时间步尚未通过完整复核'
if comparison and comparison['passed']:
    current=next(t for t in tasks if t['id']=='SEQ-01')
    current.update(title='完成 C→D 按住—释放—换位—再按住基线',status='done',
        detail='单次初始化、不重置。C 原速、D 半速，中间规划过渡；正常与减半时间步均通过，平均品丝力最大差异0.012%，峰值差异0.023%。',
        accept='本次候选接触任务转换已通过；未验证完整音乐和弦、重复往返、其他转换或未见片段泛化。')
    current_phase=next(p for p in phases if p['id']=='sequence')
    current_phase.update(status='scoped',tag='一个 C→D 转换限定通过')
for src,dst in [('multiview.mp4','transition-c-d.mp4'),('multiview_still.png','transition-c-d.png'),('transition_forces.png','transition-c-d-forces.png')]:
    shutil.copy2(transition_folder/src,ASSETS/dst)
# Latest reviewed state; legacy clips remain explicitly historical evidence.
next(p for p in phases if p['id']=='foundation').update(status='open',tag='当前优先：弦模型验证')
next(p for p in phases if p['id']=='sequence').update(status='open',tag='1.5秒转换严格验收未过')
next(p for p in phases if p['id']=='plucking').update(status='open',tag='右手已释放；声学/峰力待验证')
next(t for t in tasks if t['id']=='SEQ-01').update(status='open',detail='最新完整1.5秒C→D两dt执行完成；D保持成立，C释放入口三个零散低品力积分步使严格验收失败。旧慢速基线见历史视频。')
next(t for t in tasks if t['id']=='INF-02').update(status='scoped',detail='冻结三个同recording新时间窗，首次2/3；不是新recording泛化。')
next(t for t in tasks if t['id']=='INF-05').update(status='open',detail='E/G首轮通过及四扰动通过；新C品位bug修复后仍目标品无力，不称robust。')
task('STR-01','foundation','校核测量与能量基线','planned','P0','弦模型草案','保留旧模型和失败证据；扣除静态预张紧能量；以解析信号检查频率/衰减拟合。','测量工具能恢复已知频率与衰减；无接触能量误差随时间步减小，数值容差执行前冻结。')
task('STR-02','foundation','小振幅空弦与阻尼候选','planned','P0','弦模型草案','真实质量；先素G弦与细E，再六弦；单模态与多模态测试；独立扫描阻尼、网格、dt。','分别报告基频、前几阶模态、衰减和收敛；Siconos实验条件与本项目参数分开；候选不称真机标定。')
task('STR-03','foundation','接回品丝与物理拨头','planned','P0','弦模型草案','先单指按住再拨，区分自由段振动、接触耗散和控制器做功；对照C三根目标弦。','检查目标品保持/打品、音高、衰减、邻弦、冲量及峰值；不能只凭静力通过。')
task('STR-04','foundation','左右手回归与接触规划','planned','P0','弦模型草案','新旧模型成对回放；复核高把位C、完整1.5秒C→D和右手自然释放；再修落点与释放入口。','不逐片段改物理参数追成功；记录退化；通过的开发结果不冒充未见数据泛化。')
task('STR-05','foundation','GPU一致性与训练成本','planned','P0','弦模型草案','CPU基准成立后比较相同模型在Warp上的支持、数值结果、吞吐与显存；不默认支持。','物理一致性和吞吐分别报告；训练模型若近似，必须单独验证并记录差异。')
# Supporting contribution candidate; humanoid guitar performance remains primary.
task('SIM-01','research','M-SIM：明确技术贡献与相关工作差距','next','P0','研究','弦乐物理与非线性接触已有工作；比较机器人双向耦合、实测、性能与控制用途。','明确新增技术或系统/基准价值；未经系统对比不使用first。')
task('SIM-02','foundation','M-SIM：标定与独立实测验证','planned','P0','物理','公开数据与lab测量分开，覆盖振动、按压、释放和打品；明确范围和不确定度。','用未拟合的弦长/品位/激励验证，报告误差分布及失败。',('STR-02','STR-03'))
task('SIM-03','foundation','M-SIM：双向接触与稳健性','planned','P0','物理','手与弦互相施力；扰动初态、张力、动作，检查能量、力、冲量与穿透。','稳定性和网格/dt收敛有证据，记录失败边界。',('STR-03',))
task('SIM-04','foundation','M-SIM：CPU/GPU与训练成本','planned','P1','计算','比较支持情况、数值一致性、吞吐、显存；训练近似独立验证。','给出性能–精度曲线，不预先承诺实时或GPU支持。',('STR-05',))
task('SIM-05','research','M-SIM：环境、数据与复现包','planned','P1','数据','版本化任务API、物理参数及同步状态/控制/接触/弦运动信号，附实测对照和失败。','sim/real/参考录音分开；拆分与来源清楚；发布前核对许可。',('SIM-02','SIM-03'))
task('SIM-06','research','M-SIM：机器人任务与迁移收益','planned','P1','评测','对比几何弦、简单物理弦、校准模型；检验按弦/拨弦与可重复台架任务。','量化控制或迁移收益；只有音色改善不足以证明机器人任务价值。',('SIM-02','SIM-03'))
project=dict(updated='2026-10-07',name='Dexterous Hand Plays Guitar',phases=phases,tasks=tasks,clips=clips,
    transition=dict(tag=transition_folder.name,status=transition_state,nominal=transition,convergence=comparison),
    verified=dict(clips=5,cases=20,passed=20,datasetFiles=50,fullDatasetValidated=False,hardwareValidated=False),
    provenance=dict(sources={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['retarget/contact_labels/shared_multifinger_release_suite_v2.json','analysis/mentor_contact_targets/shared_release_suite_v2_report.json']},source='Saved project reports; shared_multifinger_release_suite_v2',kind='Manual contact-task regression',motion='Pei Xu dataset mocap → IK → bounded motors → MuJoCo contact',
                    caveats=['Candidate contact labels are manually specified, not human contact ground truth.','Per-clip tuning and source-speed scaling are disclosed.','No learned policy, G1 execution or acoustic success is established by this benchmark.']))
project['promisingContributionCandidate']=dict(id='C1',milestone='M-SIM',status='supporting_candidate_not_achieved',title='Experimentally validated string–robot interaction simulation and benchmark',scope='Guitar first; bowed instruments future extension',tasks=[f'SIM-{i:02d}' for i in range(1,7)],firstClaim=False)
project['latestReview'] = dict(status='planning_only', priority='string_model_validation', holdout='2/3 first attempts; same-recording windows', transition='1.5s strict FAIL', acoustics='not passed', rightHand='release without self-contact; peak force not converged', gpuValidated=False)
project['verified']['scope']='historical shared_release_suite_v2 only'
project['latestReview']['status']='g_string_comparison_complete_main_model_unchanged'
project['latestReview']['stringBenchmark']=read('analysis/g_string_reference_v1/status.json')
project['latestReview']['stringBenchmark']['modal_dt_comparison']=read('analysis/g_string_reference_v1/modal_dt_comparison.json')
project['latestReview']['handInteraction']=read('analysis/string_hand_interaction_v1/status.json')
project['latestReview']['status']='single_string_hand_interaction_complete_main_model_unchanged'
project['latestReview']['contactRegression']=read('analysis/string_hand_interaction_v2/current_summary.json')
project['latestReview']['status']='multistring_dt_batch_finished_not_converged'
project['latestReview']['contactBenchmark']=read('analysis/contact_benchmark_v1/status.json')
project['latestReview']['handModelRegression']=read('analysis/hand_model_regression_v1/status.json')
project['latestReview']['status']='hand_model_regression_complete_physics_sensitivity_unresolved'
# Current control-focused scope supersedes the previous acoustic-first priority.
project['latestReview']['priority']='dual_hand_control_contact_release'
project['latestReview']['dualHandContact']=read('analysis/dual_hand_contact_v1/status.json')
project['latestReview']['status']='dual_hand_quick_check_'+project['latestReview']['dualHandContact']['state']
project['latestReview']['pickRoute']=read('analysis/pick_route_v1/status.json')
project['latestReview']['status']='fixed_pick_first_contact_checks_complete'
project['latestReview']['priority']='shared_posture_fingerstyle_and_continuous_pick'
project['latestReview']['fingerstyle']=read('analysis/fingerstyle_v1/summary.json')
project['latestReview']['pickExtension']=read('analysis/pick_extension_v1/status.json')
project['latestReview']['status']='both_right_hand_methods_independent_contact_checks_complete'
next(p for p in phases if p['id']=='foundation').update(status='open',tag='接触力学底线；精细音色后置')
next(p for p in phases if p['id']=='bimanual').update(status='open',tag='当前：左C按住＋右手拨弦')
next(p for p in phases if p['id']=='plucking').update(status='open',tag='进入双手同场景接触检查')
(ASSETS/'project.json').write_text(json.dumps(project,ensure_ascii=False,indent=2)+'\n')
(ASSETS/'evidence.json').write_text(json.dumps(dict(updated=project['updated'],verified=project['verified'],clips=clips,transition=project['transition'],provenance=project['provenance']),ensure_ascii=False,indent=2)+'\n')

status_labels={'done':'已完成','scoped':'限定通过','next':'下一步','planned':'计划中','open':'待解决','deferred':'延期'}
phase_names={p['id']:p['title'] for p in phases}
def badge(status): return f'<span class="status {status}">{status_labels[status]}</span>'

phase_html=''.join(f'''<article class="phase" id="phase-{p['id']}"><div class="phase-number">{p['n']}</div><div><div class="phase-top">{badge(p['status'])}<span>{esc(p['tag'])}</span></div><h3>{esc(p['title'])}</h3><p>{esc(p['goal'])}</p><details><summary>产物与验收条件</summary><div class="detail-body"><p><b>产物</b> {esc(p['deliverable'])}</p><p><b>验收</b> {esc(p['gate'])}</p></div></details></div></article>''' for p in phases)
task_html=''.join(f'''<details class="task" id="task-{t['id']}" data-status="{t['status']}" data-priority="{t['priority']}" data-phase="{t['phase']}"><summary><span class="task-id">{t['id']}</span><span class="task-title">{esc(t['title'])}</span><span class="priority {t['priority'].lower()}">{t['priority']}</span>{badge(t['status'])}</summary><div class="task-detail"><div class="task-meta"><span>{esc(t['lane'])}</span><span>{esc(phase_names[t['phase']])}</span></div><p>{esc(t['detail'])}</p><p class="accept"><b>完成条件</b> {esc(t['accept'])}</p><div class="dependencies">依赖：{', '.join(f'<a href="#task-{d}">{d}</a>' for d in t['depends']) or '无前置任务'}</div></div></details>''' for t in tasks)
table_html=''.join(f'''<tr><th scope="row">{c['name']}</th><td>{c['fingers']} 指 · {esc(c['title'])}</td><td>{c['sourceFrames'][0]}–{c['sourceFrames'][1]}</td><td>{c['speed']:g}×</td>{''.join('<td class="pass"><span aria-label="通过">✓</span></td>' for _ in c['cases'])}</tr>''' for c in clips)
template=Path(__file__).with_name('page.template.html').read_text()
replacements={'PHASES':phase_html,'TASKS':task_html,'BENCHMARK':table_html,'TASK_COUNT':str(len(tasks)),
              'TRANSITION_STATE':esc(transition_state),
              'PHASE_OPTIONS':''.join(f'<option value="{p["id"]}">{p["n"]} {esc(p["title"])}</option>' for p in phases),
              'CLIP_OPTIONS':''.join(f'<option value="{c["id"]}">{c["name"]} · {esc(c["title"])}</option>' for c in clips),
              'PROJECT_JSON':json.dumps(project,ensure_ascii=False).replace('<','\\u003c')}
for key,value in replacements.items():template=template.replace('{{'+key+'}}',value)
assert '{{' not in template
(SITE/'projects/dexterous-guitar.html').write_text(template)
hub=SITE/'index.html';s=hub.read_text()
if 'projects/dexterous-guitar.html' not in s:
    s=s.replace('3 project(s) · 1 paper list · 19 item(s)','4 project(s) · 1 paper list · project plans & experiment reports')
    card='''<a class="card" href="projects/dexterous-guitar.html"><div class="badge proj">PROJECT</div><div class="t">Dexterous Hand Plays Guitar</div><div class="m">完整路线图 · 任务与验收 · 5 段 / 20 项物理回归 · 仿真视频</div><div class="d">→ open project workspace</div></a>'''
    s=s.replace('<div class="grid">','<div class="grid">'+card,1);hub.write_text(s)
print(f'Built guitar page: {len(phases)} phases, {len(tasks)} tasks, {len(clips)} clips; verified20/20.')
