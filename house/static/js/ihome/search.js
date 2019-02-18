var cur_page = 1; // 当前页
var next_page = 1; // 下一页
var total_page = 1;  // 总页数
var user_data_querying = true;   // 是否正在向后台获取数据

// 解析url中的查询字符串
function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

// 更新用户点选的筛选条件
function updateFilterDateDisplay(action) {
    var startDate = $("#start-date").val();
    var endDate = $("#end-date").val();
    var $filterDateTitle = $(".filter-title-bar>.filter-title").eq(0).children("span").eq(0);
    if (startDate) {
        var text = startDate.substr(5) + "/" + endDate.substr(5);
        $filterDateTitle.html(text);
    } else {
        $filterDateTitle.html("入住日期");
    }
}


// 更新房源列表信息
// action表示从后端请求的数据在前端的展示方式
// 默认采用追加方式
// action=renew 代表页面数据清空从新展示
function updateHouseData(action) {
    var areaId = $(".filter-area>li.active").attr("area-id");
    if (undefined == areaId){
        areaId = ""
        $(".filter-title-bar>.filter-title").eq(1).children("span").eq(0).text('全部')
    };
    var startDate = $("#start-date").val();
    var endDate = $("#end-date").val();
    var sortKey = $(".filter-sort>li.active").attr("sort-key");
    console.log(sortKey)
    var params = {
        aid:areaId,
        sd:startDate,
        ed:endDate,
        sk:sortKey,
        p:next_page
    };
    //发起ajax请求，获取数据，并显示在模板中
    findByArea(params)
}

function findByArea(d){
    var aname = $(".filter-title-bar>.filter-title").eq(1).children("span").eq(0).text()
    var url = '/house/search?'
    url += 'aid='+d.aid+'&'
    url += 'aname='+aname+'&'
    url += 'sd='+d.sd+'&'
    url += 'ed='+d.ed+'&'
    url += 'sortKey='+d.sk
    location.href = url
}

$(document).ready(function(){
    sort_obj = {'new': '最新上线', 'booking': '入住最多', 'price-inc': '价格 低-高', 'price-des': '价格 高-低'}
    var queryData = decodeQuery();
    var startDate = queryData["sd"];
    var endDate = queryData["ed"];
    $("#start-date").val(startDate);
    $("#end-date").val(endDate);
    updateFilterDateDisplay();
    var areaName = queryData["aname"];
    var aid = queryData["aid"];

    if (!areaName) areaName = "位置区域";
    $(".filter-title-bar>.filter-title").eq(1).children("span").eq(0).html(areaName);
    var sort_key = queryData['sortKey']
    if(!sort_key){
        sort_key = '最新上线'
    }else{
        sort_key = sort_obj[sort_key]
    }
    $(".filter-title-bar>.filter-title").eq(2).children("span").eq(0).html(sort_key);

    $(".input-daterange").datepicker({
        format: "yyyy-mm-dd",
        startDate: "today",
        language: "zh-CN",
        autoclose: true
    });
    var $filterItem = $(".filter-item-bar>.filter-item");
    $(".filter-title-bar").on("click", ".filter-title", function(e){
        var index = $(this).index();
        if (!$filterItem.eq(index).hasClass("active")) {
            $(this).children("span").children("i").removeClass("fa-angle-down").addClass("fa-angle-up");
            $(this).siblings(".filter-title").children("span").children("i").removeClass("fa-angle-up").addClass("fa-angle-down");
            $filterItem.eq(index).addClass("active").siblings(".filter-item").removeClass("active");
            $(".display-mask").show();
        } else {
            $(this).children("span").children("i").removeClass("fa-angle-up").addClass("fa-angle-down");
            $filterItem.eq(index).removeClass('active');
            $(".display-mask").hide();
            updateFilterDateDisplay();
        }
    });
    $(".display-mask").on("click", function(e) {
        $(this).hide();

        cur_page = 1;
        next_page = 1;
        total_page = 1;
        updateHouseData("renew");

    });
    $(".filter-item-bar>.filter-area").on("click", "li", function(e) {
        if (!$(this).hasClass("active")) {
            $(this).addClass("active");
            $(this).siblings("li").removeClass("active");
            $(".filter-title-bar>.filter-title").eq(1).children("span").eq(0).html($(this).html());
        } else {
            $(this).removeClass("active");
            $(".filter-title-bar>.filter-title").eq(1).children("span").eq(0).html("位置区域");
        }
    });
    $(".filter-item-bar>.filter-sort").on("click", "li", function(e) {
        if (!$(this).hasClass("active")) {
            $(this).addClass("active");
            $(this).siblings("li").removeClass("active");
            $(".filter-title-bar>.filter-title").eq(2).children("span").eq(0).html($(this).html());
        }
    })

    $.post('/house/appoint_search/', 'json', function(data){
            areas = data.data.areas_list

            for(a in areas){
                active = areas[a].id == aid ? 'class="active"':'';
                l = '<li area-id="'+areas[a].id+'" '+ active +'>'+areas[a].name+'</li>'
                $('.filter-area').append(l)
            }
            houses = data.data.houses_list
            for(h in houses){
                li = '<li class="house-item"><a href="/house/detail/'+houses[h].id+'">'
                li += '<img src="/static/media/'+houses[h].image+'"></a>'
                li += '<div class="house-desc"><div class="landlord-pic">'
                li += '<img src="/static/media/'+houses[h].user_avatar+'"></div>'
                li += '<div class="house-price">￥<span>'+houses[h].price+'</span>/晚</div>'
                li += '<div class="house-intro"><span class="house-title">'+houses[h].title+'</span>'
                li += '<em>出租'+houses[h].room_count+'间 - 1次入住 - '+houses[h].address+'</em></div></div></li>'
                $('.house-list').append($(li))
            }
        })


})